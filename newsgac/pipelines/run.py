import numpy

from sklearn.model_selection import KFold, cross_val_predict

from newsgac import config
from newsgac.pipelines.models import Result

def run_pipeline(pipeline):
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])
    pipeline.sk_pipeline = pipeline.get_sk_pipeline()
    pipeline.sk_pipeline.fit(texts, labels)
    pipeline.result = validate(
        pipeline.sk_pipeline,
        texts,
        labels
    )
    pipeline.save()


def validate(model, X, labels):
    cv = KFold(n_splits=10, random_state=42, shuffle=True)
    cross_val_predictions = cross_val_predict(model, X, labels, cv=cv, n_jobs=config.cross_val_n_jobs)
    return Result.from_prediction(labels, cross_val_predictions)
