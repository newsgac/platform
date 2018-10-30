import numpy

from sklearn.model_selection import KFold, cross_val_predict

from newsgac.pipelines.models import Result

from newsgac.data_engineering.utils import LABEL_DICT

def run_pipeline(pipeline):
    # INVERT LABEL DICT
    inv_labels = {v: k for k, v in LABEL_DICT.iteritems()}
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([inv_labels[article.label] for article in pipeline.data_source.articles])

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
    cross_val_predictions = cross_val_predict(model, X, labels, cv=cv)
    return Result.from_prediction(labels, cross_val_predictions)
