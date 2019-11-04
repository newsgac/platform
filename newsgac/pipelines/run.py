import numpy

from sklearn.model_selection import KFold, cross_val_predict

from newsgac import config
from newsgac.pipelines.models import Result, Pipeline

import logging
logger = logging.getLogger(__name__)

def run_pipeline(pipeline: Pipeline):
    logger.info(('Running pipeline ' + str(pipeline.pk)))
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])
    sk_pipeline = pipeline.get_sk_pipeline()
    logger.info("Fitting pipeline")
    sk_pipeline.fit(texts, labels)
    pipeline.sk_pipeline = sk_pipeline
    logger.info("Validating pipeline")
    pipeline.result = validate(
        sk_pipeline,
        texts,
        labels
    )
    pipeline.save()


def validate(model, X, labels):
    # TODO: use stratified kfold
    cv = KFold(n_splits=10, random_state=42, shuffle=True)
    cross_val_predictions = cross_val_predict(model, X, labels, cv=cv, n_jobs=config.n_cross_val_jobs)
    return Result.from_prediction(labels, cross_val_predictions)
