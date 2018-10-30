from sklearn.pipeline import FeatureUnion, Pipeline as SKPipeline
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from newsgac.learners import LearnerNB
from newsgac.nlp_tools import TFIDF, Frog
from newsgac.nlp_tools.transformers import CleanOCR, StopWordRemoval, ApplyLemmatization, ExtractBasicFeatures, \
    ExtractSentimentFeatures


def get_sk_pipeline(sw_removal, lemmatization, nlp_tool, learner):
    skl_steps = [('CleanOCR', CleanOCR())]

    feature_names = []

    if sw_removal:
        skl_steps.append(('StopWordRemoval', StopWordRemoval()))

    if lemmatization:
        skl_steps.append(('Lemmatization', ApplyLemmatization()))

    if nlp_tool:
        feature_pipelines = []
        if type(nlp_tool) != TFIDF:
            feature_pipelines = [
                ('BasicFeatures', ExtractBasicFeatures()),
                ('SentimentFeatures', ExtractSentimentFeatures()),
            ]

            feature_names += ExtractBasicFeatures.get_feature_names()
            feature_names += ExtractSentimentFeatures.get_feature_names()

        feature_pipelines.append(
            (nlp_tool.name, nlp_tool.get_feature_extractor())
        )
        skl_steps.append(
            ('FeatureExtraction', FeatureUnion(feature_pipelines))
        )

        if nlp_tool.parameters.scaling:
            skl_steps.append(('RobustScaler', RobustScaler(with_centering=False)))

        # NB Can't handle negative feature values.
        if isinstance(learner, LearnerNB) and isinstance(nlp_tool, Frog):
            skl_steps.append(('MinMaxScaler', MinMaxScaler(feature_range=(0, 1))))

    skl_steps.append(('Classifier', learner.get_classifier()))
    return SKPipeline(skl_steps)
