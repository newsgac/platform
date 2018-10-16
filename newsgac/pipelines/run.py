import numpy

from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline as SKPipeline, FeatureUnion
from sklearn.preprocessing import RobustScaler, MaxAbsScaler

from newsgac.learners import LearnerNB
from newsgac.learners.models.learner import Result
from newsgac.nlp_tools import TFIDF
from newsgac.nlp_tools.transformers import StopWordRemoval, ApplyLemmatization, CleanOCR, ExtractBasicFeatures, \
    ExtractSentimentFeatures
from newsgac.tasks.progress import report_progress


def dict_vectorize(transformer_name, transformer):
    return (transformer_name, SKPipeline([
        (transformer_name, transformer), ('DictVectorizer', DictVectorizer())
    ]))


def get_sk_pipeline(pipeline):
    skl_steps = [('CleanOCR', CleanOCR())]

    if pipeline.sw_removal:
        skl_steps.append(('StopWordRemoval', StopWordRemoval()))

    if pipeline.lemmatization:
        skl_steps.append(('Lemmatization', ApplyLemmatization()))

    if pipeline.nlp_tool:
        feature_pipelines = []
        if type(pipeline.nlp_tool) != TFIDF:
            feature_pipelines = [
                dict_vectorize('BasicFeatures', ExtractBasicFeatures()),
                dict_vectorize('SentimentFeatures', ExtractSentimentFeatures()),
            ]
        feature_pipelines.append(
            dict_vectorize(pipeline.nlp_tool.name, pipeline.nlp_tool)
        )
        skl_steps.append(
            ('FeatureExtraction', FeatureUnion(feature_pipelines))
        )

        if pipeline.nlp_tool.parameters.scaling:
            skl_steps.append(('RobustScaler', RobustScaler(with_centering=False)))

        # NB Can't handle negative feature values.
        if isinstance(pipeline.learner, LearnerNB):
            skl_steps.append(('MaxAbsScaler', MaxAbsScaler()))

    skl_steps.append(('Classifier', pipeline.learner.get_classifier()))
    return SKPipeline(skl_steps)


def run_pipeline(pipeline):
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])

    pipeline.sk_pipeline = get_sk_pipeline(pipeline)

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
