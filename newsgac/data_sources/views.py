from bokeh.embed import components
from bson import ObjectId
from flask import Blueprint, render_template, request, session, url_for, flash
from pymodm.errors import ValidationError
from werkzeug.utils import redirect, secure_filename

from newsgac.common.back import back
from newsgac.pipelines.models import Pipeline
from newsgac.users.view_decorators import requires_login
from newsgac.data_sources.models import DataSource
from newsgac.stop_words.models import StopWords
from newsgac.data_sources.tasks import process_data_source
from newsgac.users.models import User
from newsgac.data_sources.plots import data_source_stats

__author__ = 'abilgin'

data_source_blueprint = Blueprint('data_sources', __name__)


@data_source_blueprint.route('/')
@requires_login
def overview():
    # todo: get users data sources only
    data_sources = list(DataSource.objects.values())
    stop_words = list(StopWords.objects.values())
    return render_template("data_sources/data_sources.html", data_sources=data_sources, stop_words=stop_words)


@data_source_blueprint.route('/new', methods=['GET', 'POST'])
@requires_login
def new():
    if request.method == 'POST':
        try:
            form_dict = request.form.to_dict()
            data_source = DataSource(**form_dict)
            data_source.filename = secure_filename(request.files['file'].filename)
            data_source.file = request.files['file']
            data_source.user = User(email=session['email'])
            data_source.save()
            flash('The file has been successfully uploaded.', 'success')
            data_source.task.set_started()
            data_source.save()
            process_data_source.delay(data_source._id)

            return redirect(url_for("data_sources.overview"))
        except ValidationError as e:
            if 'filename' in e.message:
                flash('The file type is not supported! Try again using the allowed file formats.', 'error')

    return render_template('data_sources/new_data_source.html', form=request.form)


@data_source_blueprint.route('/<string:data_source_id>')
@requires_login
def view(data_source_id):
    data_source = DataSource.objects.get({'_id': ObjectId(data_source_id)})
    script, div = None, None
    try:
        plot = data_source_stats(data_source)
        script, div = components(plot)

    except Exception:
        pass

    return render_template(
        'data_sources/data_source.html',
        data_source=data_source,
        plot_script=script,
        plot_div=div,
        mimetype='text/html'
    )


#todo: write test for this
@data_source_blueprint.route('/<string:data_source_id>/delete')
@requires_login
def delete(data_source_id):
    data_source = DataSource.objects.get({'_id': ObjectId(data_source_id)})
    pipelines_using_data_source = list(Pipeline.objects.raw({'data_source': data_source.pk}))

    if len(pipelines_using_data_source) > 0:
        error = "There are existing pipelines using this data source ("+ \
                str(data_source.display_title)+ "). Please delete the pipelines connected with this data source first!"
        flash(error, 'error')
        return redirect((url_for('pipelines.overview')))

    data_source.delete()
    return redirect((url_for('data_sources.overview')))


@data_source_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for data_source in DataSource.objects.all():
        data_source.delete()
    return back.redirect()
