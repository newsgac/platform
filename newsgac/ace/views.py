from __future__ import absolute_import
from bson import ObjectId
from flask import Blueprint, render_template, request, url_for, redirect, session

from newsgac.ace.models import ACE
from newsgac.common.back import back
from newsgac.common.cached_view import cached_view
from newsgac.common.utils import model_to_dict
from newsgac.data_engineering.utils import genre_codes
from newsgac.pipelines.models import Pipeline
from newsgac.data_sources.models import DataSource
from newsgac.users.models import User
from newsgac.users.view_decorators import requires_login
from newsgac.ace.tasks import run_ace, explain_article_lime_task

ace_blueprint = Blueprint('ace', __name__)


@ace_blueprint.route('/')
@requires_login
@back.anchor
def overview():
    aces = [
        {
            'id': str(ace._id),
            'created': ace.created,
            'display_title': ace.display_title,
            'data_source': {
                'display_title': ace.data_source.display_title
            },
            'task': ace.task,

        } for ace in list(ACE.objects.all())
    ]

    # data_sources = list(DataSource.objects.all())
    data_sources = list(DataSource.objects.raw({'training_purpose': False}))
    pipelines = list(Pipeline.objects.all())
    return render_template(
        "ace/overview.html",
        aces=aces,
        pipelines=pipelines,
        data_sources=data_sources,
    )


@ace_blueprint.route('/new', methods=['GET'])
@requires_login
@back.anchor
def new():
    data_sources = list(DataSource.objects.all())
    pipelines = list(Pipeline.objects.all())
    return render_template(
        "ace/overview.html",
        pipelines=pipelines,
        data_sources=data_sources,
    )


@ace_blueprint.route('/new', methods=['POST'])
@requires_login
def new_save():
    ace = ACE()
    ace.data_source = DataSource.objects.get({'_id': ObjectId(request.form['data_source'])})
    ace.pipelines = [Pipeline.objects.get({'_id': ObjectId(pipeline_id)}) for pipeline_id in request.form.getlist('pipelines[]')]
    ace.user = User(email=session['email'])
    ace.display_title = ace.data_source.display_title + ' (' + ', '.join(p.display_title for p in ace.pipelines) + ')'
    ace.save()
    task = run_ace.delay(str(ace._id))
    ace.task_id = task.task_id
    ace.save()
    return redirect(url_for('ace.overview'))


@ace_blueprint.route('/<string:ace_id>')
@requires_login
def view(ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    pipelines = [model_to_dict(pipeline) for pipeline in ace.pipelines]
    articles = [{
        'raw_text': article.raw_text.encode('utf-8'),
        'predictions': [genre_codes[p] for p in ace.predictions[idx]],
        'label': genre_codes[article.label],
    } for idx, article in enumerate(ace.data_source.articles)]

    return render_template(
        "ace/run.html",
        # ace=ace,
        # genre_codes=genre_codes,
        # genre_labels=genre_labels,
        ace_id=ace_id,
        pipelines=pipelines,
        articles=articles
    )


@ace_blueprint.route('/<string:ace_id>/delete')
@requires_login
def delete(ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    ace.delete()

    return back.redirect()


@ace_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for ace in list(ACE.objects.all()):
        ace.delete()

    return back.redirect()


# article number is an integer, but you should leave string here so that we can
# generate a url template that can be used dynamically from Javascript
@ace_blueprint.route('/<string:ace_id>/explain_features_lime/<string:pipeline_id>/<string:article_number>')
@requires_login
def explain_article(*args, **kwargs):
    return cached_view(
        template='pipelines/explain.html',
        view_name='explain_article',
        task=explain_article_lime_task,
        args=args,
        kwargs=kwargs
    )
