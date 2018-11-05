from sklearn.pipeline import FeatureUnion, Pipeline as SKPipeline
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from newsgac.learners import LearnerNB
from newsgac.learners.models.learner import Learner
from newsgac.nlp_tools import TFIDF, Frog
from newsgac.nlp_tools.models.nlp_tool import NlpTool
from newsgac.nlp_tools.transformers import CleanOCR, StopWordRemoval, ApplyLemmatization, ExtractBasicFeatures, \
    ExtractSentimentFeatures


def get_sk_pipeline(sw_removal, lemmatization, nlp_tool, learner):
    """
    Transform our `newsgac.pipelines.models.Pipeline` into a Scikit Learn `sklearn.pipeline.Pipeline`

    :param sw_removal: If true, add stop word removal step
    :type sw_removal: bool

    :param lemmatization: If true, add lemmatization step
    :type lemmatization: bool
    :param nlp_tool: NlpTool to use extract features from text (Frog / TFIDF)
    :type nlp_tool: NlpTool
    :param learner: Learner is the classifier
    :type learner: Learner
    :return: Scikit Learn pipeline
    """
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
