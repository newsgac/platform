from bson import ObjectId
from flask import Blueprint, render_template, request, session, url_for, flash, send_file
from pymodm.errors import ValidationError
from werkzeug.utils import redirect, secure_filename

from newsgac.common.back import back
from newsgac.stop_words.models import StopWords
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User

stop_words_blueprint = Blueprint('stop_words', __name__)


@stop_words_blueprint.route('/')
@requires_login
def overview():
    # todo: get users data sources only
    stop_words = list(StopWords.objects.values())
    return render_template("stop_words/stop_words.html", stop_words=stop_words)


@stop_words_blueprint.route('/new', methods=['GET', 'POST'])
@requires_login
def new():
    if request.method == 'POST':
        try:
            form_dict = request.form.to_dict()
            stop_words = StopWords(**form_dict)
            stop_words.filename = secure_filename(request.files['file'].filename)
            stop_words.file = request.files['file']
            stop_words.user = User(email=session['email'])
            stop_words.save()
            flash('The file has been successfully uploaded.', 'success')

            return redirect(url_for("stop_words.overview"))
        except ValidationError as e:
            if 'filename' in e.message:
                flash('The file type is not supported! Try again using the allowed file formats.', 'error')

    return render_template('stop_words/new_stop_words.html', form=request.form)


#todo: write test for this
@stop_words_blueprint.route('/<string:stop_words_id>/delete')
@requires_login
def delete(stop_words_id):
    stop_words = StopWords.objects.get({'_id': ObjectId(stop_words_id)})
    stop_words.delete()
    return redirect((url_for('stop_words.overview')))



#todo: write test for this
@stop_words_blueprint.route('/<string:stop_words_id>/download')
@requires_login
def download(stop_words_id):
    stop_words = StopWords.objects.get({'_id': ObjectId(stop_words_id)})
    return send_file(stop_words.file, 'text/plain', as_attachment=True, attachment_filename=stop_words.filename)


@stop_words_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for stop_words in StopWords.objects.all():
        stop_words.delete()
    return back.redirect()
