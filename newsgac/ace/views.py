from __future__ import absolute_import
from bson import ObjectId
from bokeh.embed import components
from bokeh.layouts import gridplot
from flask import Blueprint, render_template, request, url_for, redirect, session, json
from lime.lime_tabular import LimeTabularExplainer

from newsgac.ace.models import ACE
from newsgac.common.back import back
from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.data_engineering.utils import genre_codes, genre_labels
from newsgac.pipelines.models import Pipeline
from newsgac.data_sources.models import DataSource
from newsgac.users.models import User
from newsgac.users.view_decorators import requires_login
from newsgac.visualisation.comparison import PipelineComparator
from newsgac.visualisation.resultvisualiser import ResultVisualiser
from newsgac.ace.tasks import run_ace

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
            'task': json.dumps(ace.task.as_dict()),

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
        'predictions': [p.encode('utf-8') for p in ace.predictions[idx]],
        'label': article.label.encode('utf-8'),
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
def explain_article_lime(ace_id, pipeline_id, article_number):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})

    skp = pipeline.sk_pipeline

    # model == learner
    model = skp.steps.pop()[1]
    feature_extractor = skp
    feature_names = skp.named_steps['FeatureExtraction'].get_feature_names()

    # calculate feature vectors:
    v = feature_extractor.transform([a.raw_text for a in pipeline.data_source.articles])

    if v.__class__.__name__ == 'csr_matrix':
        v = v.toarray()

    explainer = LimeTabularExplainer(
        training_data=v,
        feature_names=feature_names,
        class_names=model.classes_
    )

    article_number = int(article_number)
    article = ace.data_source.articles[article_number]
    article_features = feature_extractor.transform([article.raw_text]).toarray()[0]
    prediction = model.predict([article_features])[0]

    exp = explainer.explain_instance(
        data_row=article_features,
        predict_fn=model.predict_proba,
        #num_features=24,
        num_samples=3000
    )

    return render_template(
        'pipelines/explain_lime.html',
        pipeline=pipeline,
        article=article,
        prediction=prediction,
        exp_html=exp.as_html(),
        article_number=article_number,
    )
