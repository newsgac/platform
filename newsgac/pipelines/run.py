import numpy

from sklearn.model_selection import KFold, cross_val_predict

from newsgac.pipelines.models import Result
from newsgac.tasks.progress import report_progress


def run_pipeline(pipeline):
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])

    pipeline.sk_pipeline = pipeline.get_sk_pipeline()

    report_progress('training', 0)
    pipeline.sk_pipeline.fit(texts, labels)
    report_progress('training', 1)

    report_progress('validating', 0)
    pipeline.result = validate(
        pipeline.sk_pipeline,
        texts,
        labels,
    )
    pipeline.save()
    report_progress('validating', 1)


def validate(model, X, labels):
    cv = KFold(n_splits=10, random_state=42, shuffle=True)
    cross_val_predictions = cross_val_predict(model, X, labels, cv=cv)
    return Result.from_prediction(labels, cross_val_predictions)
