from sklearn.pipeline import FeatureUnion, Pipeline as SklearnPipeline
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from newsgac.learners import LearnerNB
from newsgac.nlp_tools import TFIDF, Frog
from newsgac.nlp_tools.transformers import CleanOCR, StopWordRemoval, ApplyLemmatization, ExtractBasicFeatures, \
    ExtractSentimentFeatures, RemoveQuotes, ExtractQuotes


class NoneStepsPipeline(SklearnPipeline):
    """
    Simple wrapper around sklearn.pipeline.Pipeline that removes any steps set to None,
    it also allows specifying a step as the step to get the feature names from, so that
    get_feature_names can be called on this pipeline.
    """
    def __init__(self, steps, memory=None, feature_names_from=None):
        self.feature_names_from = feature_names_from
        steps = [step for step in steps if step is not None]
        super(NoneStepsPipeline, self).__init__(steps, memory)

    def get_feature_names(self):
        if self.feature_names_from:
            return self.named_steps[self.feature_names_from].get_feature_names()
        raise ValueError('No feature_names_from specified, cannot get feature names')


def get_sk_pipeline(pipeline):
    """
    Transform our `newsgac.pipelines.models.Pipeline` into a Scikit Learn `sklearn.pipeline.Pipeline`
    """
    if type(pipeline.nlp_tool) == TFIDF:
        return NoneStepsPipeline(
            steps=[
                ('CleanOCR', CleanOCR()),
                ('StopWordRemoval', StopWordRemoval()) if pipeline.sw_removal else None,
                ('Lemmatization', ApplyLemmatization()) if pipeline.lemmatization else None,
                ('FeatureExtraction', FeatureUnion([
                    ('TFIDF', NoneStepsPipeline(
                        steps=[
                            ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                            (pipeline.nlp_tool.name, pipeline.nlp_tool.get_feature_extractor())
                        ],
                        feature_names_from=pipeline.nlp_tool.name
                    ))
                ])),
                ('RobustScaler', RobustScaler(with_centering=False)) if pipeline.nlp_tool.parameters.scaling else None,
                ('Classifier', pipeline.learner.get_classifier())
            ],
            feature_names_from='FeatureExtraction'
        )

    if type(pipeline.nlp_tool) == Frog:
        return NoneStepsPipeline(
            steps=[
                ('CleanOCR', CleanOCR()),
                ('StopWordRemoval', StopWordRemoval()) if pipeline.sw_removal else None,
                ('Lemmatization', ApplyLemmatization()) if pipeline.lemmatization else None,
                ('FeatureExtraction', FeatureUnion([
                    ('Basic', ExtractBasicFeatures()),
                    ('Quote', ExtractQuotes()),
                    ('Sentiment', NoneStepsPipeline(
                        steps=[
                            ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                            ('SentimentFeatures', ExtractSentimentFeatures())
                        ],
                        feature_names_from='SentimentFeatures'
                    )),
                    ('Frog', NoneStepsPipeline(
                        steps=[
                            ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                            (pipeline.nlp_tool.name, pipeline.nlp_tool.get_feature_extractor())
                        ],
                        feature_names_from=pipeline.nlp_tool.name
                    ))
                ])),
                ('RobustScaler', RobustScaler(with_centering=False)) if pipeline.nlp_tool.parameters.scaling else None,
                ('MinMaxScaler', MinMaxScaler(feature_range=(0, 1))) if isinstance(pipeline.learner, LearnerNB) else None,
                ('Classifier', pipeline.learner.get_classifier())
            ],
            feature_names_from='FeatureExtraction'
        )

    raise ValueError('Cannot create ScikitLearn Pipeline for nlp_tool %s' % str(pipeline.nlp_tool))
