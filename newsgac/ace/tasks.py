import hashlib
import sys

import numpy
from bson import ObjectId
from flask import render_template
from lime.lime_tabular import LimeTabularExplainer

from newsgac.cached_views.models import CachedView
from newsgac.pipelines import Pipeline
from newsgac.tasks.models import Status

from newsgac.ace.models import ACE
from newsgac.tasks.celery_app import celery_app, ResultTask


def get_predictions(articles, pipelines):
    # todo: parallelize
    # pipeline predictions are (hopefully) already parallelized for multiple articles at the same time
    # we could still paralellize multiple pipelines
    predictions = []
    for idx, pipeline in enumerate(pipelines):
        predictions.append(
            pipeline.sk_pipeline.predict([article.raw_text for article in articles]))
    # transpose so first axis is now article e.g. predictions[0][1] is article 0, pipeline 1
    return numpy.array(predictions).transpose()


@celery_app.task(bind=True, trail=True)
def run_ace(self, ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    ace.task.set_started()
    ace.save()
    try:
        ace.predictions = get_predictions(ace.data_source.articles, ace.pipelines)
        ace.task.set_success()
        ace.save()
    except Exception as e:
        t, v, tb = sys.exc_info()
        ace.task.status = Status.FAILURE
        ace.task.set_failure(e)
        ace.save()
        raise t, v, tb


@celery_app.task(bind=True)
def explain_article_lime_task(self, view_cache_id, ace_id, pipeline_id, article_number):
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
        # num_features=24,
        num_samples=3000
    )

    cache = CachedView.objects.get({'_id': ObjectId(view_cache_id)})
    cache.task.set_success()
    cache.data = dict(
        pipeline=pipeline,
        article=article,
        prediction=prediction,
        exp_html=exp.as_html(),
        article_number=article_number,
    )
    cache.save()
