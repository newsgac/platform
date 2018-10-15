import numpy
import hashlib

from pymodm.errors import DoesNotExist

from sklearn.externals.joblib import delayed
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from newsgac.learners import LearnerNB
from newsgac.learners.models.learner import Result
from newsgac.caches.models import Cache
from newsgac.common.json_encoder import _dumps
from newsgac.pipelines.data_engineering.preprocessing import remove_stop_words, apply_lemmatization
from newsgac.tasks.progress import report_progress
from newsgac.parallel_with_progress import ParallelWithProgress


n_parallel_jobs = 8

# def apply_clean_ocr(article):
#     article['text'] = get_clean_ocr(article['text'])


def get_pipeline_features_cache_hash(pipeline):
    pipeline_dict = pipeline.to_son().to_dict()
    pipeline_cache_repr = {
        'nlp_tool': pipeline_dict['nlp_tool'],
        'sw_removal': pipeline_dict['sw_removal'],
        'lemmatization': pipeline_dict['lemmatization'],
        'data_source_id': str(pipeline_dict['data_source'])
    }
    return hashlib.sha1(_dumps(pipeline_cache_repr)).hexdigest()


def set_features(pipeline):
    articles = [
        article.raw_text for article in pipeline.data_source.articles
    ]

    if len(articles) == 0:
        raise ValueError('No articles in data source')

    pipeline_features_cache_hash = get_pipeline_features_cache_hash(pipeline)

    try:
        pipeline.features = Cache.objects.get({'hash': pipeline_features_cache_hash})

    except DoesNotExist:
        # ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
        #     delayed(apply_clean_ocr)(a) for a in articles
        # )
        if pipeline.sw_removal:
            articles = ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
                delayed(remove_stop_words)(a) for a in articles
            )

        if pipeline.lemmatization:
            articles = ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
                delayed(apply_lemmatization)(a) for a in articles
            )

        if pipeline.nlp_tool:
            feature_names, features = pipeline.nlp_tool.get_features(articles)
            pipeline.features = Cache(
                hash=pipeline_features_cache_hash,
                data={
                    'names': feature_names,
                    'values': features,
                }
            )
            pipeline.features.save()
            pipeline.save()


def run_pipeline(pipeline):
    set_features(pipeline)
    features = pipeline.features.data['values']
    feature_names = pipeline.features.data['names']
    labels = numpy.array([article.label for article in pipeline.data_source.articles])

    sklSteps = []
    if pipeline.nlp_tool.parameters.scaling:
        sklSteps.append(('RobustScaler', RobustScaler()))

    # NB Can't handle negative feature values. todo: abstract this?
    if isinstance(pipeline.learner, LearnerNB):
        sklSteps.append(('MinMaxScaler', MinMaxScaler(feature_range=(0, 1))))

    sklSteps.append(('Classifier', pipeline.learner.get_classifier()))

    report_progress('training', 0)
    pipeline.learner.trained_model = SKPipeline(sklSteps).fit(features, labels)
    report_progress('training', 1)

    report_progress('validating', 0)
    pipeline.learner.result = validate(
        pipeline.learner.trained_model,
        features,
        labels,
    )
    pipeline.save()
    report_progress('validating', 1)


def validate(model, features, labels):
    cv = KFold(n_splits=10, random_state=42, shuffle=True)
    cross_val_predictions = cross_val_predict(model, features, labels, cv=cv)
    return Result.from_prediction(labels, cross_val_predictions)
