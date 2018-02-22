from __future__ import absolute_import

import time
from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect
from src.app import app
from src.celery_tasks.tasks import process_data, del_data
from src.common.database import Database
from src.models.data_sources.data_source import DataSource
import src.models.data_sources.errors as DataSourceErrors
from src.common.back import back
import src.models.users.decorators as user_decorators
from werkzeug.utils import secure_filename
import src.data_engineering.utils as DataUtils

__author__ = 'abilgin'

DATABASE = Database()

data_source_blueprint = Blueprint('data_sources', __name__)

@data_source_blueprint.route('/')
@user_decorators.requires_login
@back.anchor
def user_data_sources():
    return render_template("data_sources/data_sources.html", data_sources = DataSource.get_by_user_email(session['email']))

@data_source_blueprint.route('/new', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_data_source():
    if request.method == 'POST':
        f = request.files['file']
        if f and DataSource.is_allowed(f.filename):
            filename = secure_filename(f.filename)
            try:
                if DataSource.is_source_unique(user_email= session['email'], display_title=request.form['display_title'],
                                        filename=filename):
                        # file_handler = DATABASE.getGridFS().put(pickle.dumps(f))
                        file_handler = DATABASE.getGridFS().put(f)
                        new_ds = DataSource(user_email= session['email'], display_title=request.form['display_title'],
                                            description=request.form['description'], secure_filename=filename, **dict(new_handler=file_handler))
                        new_ds.save_to_db()
                        flash('The file has been successfully uploaded.', 'success')
                        return redirect(url_for("data_sources.user_data_sources"))

            except DataSourceErrors.ResourceError as e:
                flash(e.message, 'error')
                return render_template('data_sources/new_data_source.html', form=request.form)
        else:
            flash('The file type is not supported! Try again using the allowed file formats.', 'error')

    return render_template('data_sources/new_data_source.html')

@data_source_blueprint.route('/<string:data_source_id>')
@user_decorators.requires_login
def get_data_source_page(data_source_id):
    # return the data source page with the type code
    ds = DataSource.get_by_id(data_source_id)

    return render_template('data_sources/data_source.html', data_source=ds)

@data_source_blueprint.route('/article/<string:article_id>')
@user_decorators.requires_login
def get_article_page(article_id):
    # display the processed data source instance which is an article
    art = DataSource.get_processed_article_by_id(article_id)

    return render_template('data_sources/article.html', article=art, descriptions=DataUtils.feature_descriptions)

@data_source_blueprint.route('/process/<string:data_source_id>')
@user_decorators.requires_login
def process_data_source(data_source_id):
    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = process_data.delay(data_source_id)
    else:
        # without celery
        DataSource.get_by_id(data_source_id).process_data_source()

    time.sleep(0.5)
    return redirect(url_for('.get_data_source_page', data_source_id=data_source_id))

@data_source_blueprint.route('/visualise/<string:data_source_id>')
@user_decorators.requires_login
def visualise_stats(data_source_id):
    ds = DataSource.get_by_id(data_source_id)
    # results = ds.get_stats()
    # plot, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results, title="")
    #
    # return render_template('experiments/results.html',
    #                        experiment=experiment,
    #                        results=results,
    #                        plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
    #                        mimetype='text/html')

    return render_template('underconstruction.html')

@data_source_blueprint.route('/overview',  methods=['GET'])
@user_decorators.requires_login
@back.anchor
def sources_overview():
    return render_template('underconstruction.html')

@data_source_blueprint.route('/delete/<string:data_source_id>')
@user_decorators.requires_login
def delete_data_source(data_source_id):
    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = del_data.delay(data_source_id)
    else:
        # without celery
        DataSource.get_by_id(data_source_id).delete()

    time.sleep(0.5)
    return back.redirect()