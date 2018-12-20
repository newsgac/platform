from sklearn.pipeline import FeatureUnion, Pipeline as SklearnPipeline
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from newsgac.learners import LearnerNB
from newsgac.nlp_tools import TFIDF, Frog, FrogTFIDF
from newsgac.nlp_tools.transformers import CleanOCR, StopWordRemoval, ApplyLemmatization, ExtractBasicFeatures, \
    ExtractSentimentFeatures, RemoveQuotes, ExtractQuotes


def features_pipeline(steps, feature_names_from=None):
    """
    Simple wrapper that creates a sklearn.pipeline.Pipeline but removes any steps set to None,
    it also allows specifying a step as the step to get the feature names from, so that
    get_feature_names can be called on this pipeline.
    """
    steps = [step for step in steps if step is not None]
    pipeline = SklearnPipeline(steps)
    if feature_names_from:
        pipeline.get_feature_names = pipeline.named_steps[feature_names_from].get_feature_names
    return pipeline



def tfidf_union(pipeline, name, feature_extractor):
    return FeatureUnion([
        ('TFIDF', features_pipeline(
            steps=[
                ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                (name, feature_extractor)
            ],
            feature_names_from=name
        ))
    ])


def frog_union(pipeline, name, feature_extractor):
    return FeatureUnion([
        ('Basic', ExtractBasicFeatures()),
        ('Quote', ExtractQuotes()),
        ('Sentiment', features_pipeline(
            steps=[
                ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                ('SentimentFeatures', ExtractSentimentFeatures())
            ],
            feature_names_from='SentimentFeatures'
        )),
        ('Frog', features_pipeline(
            steps=[
                ('RemoveQuotes', RemoveQuotes()) if pipeline.quote_removal else None,
                (name, feature_extractor)
            ],
            feature_names_from=name
        ))
    ])

def get_sk_pipeline(pipeline):
    """
    Transform our `newsgac.pipelines.models.Pipeline` into a Scikit Learn `sklearn.pipeline.Pipeline`
    """
    if type(pipeline.nlp_tool) == TFIDF:
        return features_pipeline(
            steps=[
                ('CleanOCR', CleanOCR()),
                ('StopWordRemoval', StopWordRemoval()) if pipeline.sw_removal else None,
                ('Lemmatization', ApplyLemmatization()) if pipeline.lemmatization else None,
                ('FeatureExtraction', tfidf_union(pipeline, pipeline.nlp_tool.name, pipeline.nlp_tool.get_feature_extractor())),
                ('RobustScaler', RobustScaler(with_centering=False)) if pipeline.nlp_tool.parameters.scaling else None,
                ('Classifier', pipeline.learner.get_classifier())
            ],
            feature_names_from='FeatureExtraction'
        )

    if type(pipeline.nlp_tool) == Frog:
        return features_pipeline(
            steps=[
                ('CleanOCR', CleanOCR()),
                ('StopWordRemoval', StopWordRemoval()) if pipeline.sw_removal else None,
                ('Lemmatization', ApplyLemmatization()) if pipeline.lemmatization else None,
                ('FeatureExtraction', frog_union(pipeline, pipeline.nlp_tool.name, pipeline.nlp_tool.get_feature_extractor())),
                ('RobustScaler', RobustScaler(with_centering=False)) if pipeline.nlp_tool.parameters.scaling else None,
                ('MinMaxScaler', MinMaxScaler(feature_range=(0, 1))) if isinstance(pipeline.learner, LearnerNB) else None,
                ('Classifier', pipeline.learner.get_classifier())
            ],
            feature_names_from='FeatureExtraction'
        )

    if type(pipeline.nlp_tool) == FrogTFIDF:
        frog = Frog()
        frog.parameters = pipeline.nlp_tool.parameters
        tfidf = TFIDF()

        return features_pipeline(
            steps=[
                ('CleanOCR', CleanOCR()),
                ('StopWordRemoval', StopWordRemoval()) if pipeline.sw_removal else None,
                ('Lemmatization', ApplyLemmatization()) if pipeline.lemmatization else None,
                ('FeatureExtraction', FeatureUnion([
                    ('frog', frog_union(pipeline, 'frog', frog.get_feature_extractor())),
                    ('tfidf', tfidf_union(pipeline, 'tfidf', tfidf.get_feature_extractor()))
                ])),
                ('RobustScaler', RobustScaler(with_centering=False)) if pipeline.nlp_tool.parameters.scaling else None,
                ('MinMaxScaler', MinMaxScaler(feature_range=(0, 1))) if isinstance(pipeline.learner,
                                                                                   LearnerNB) else None,
                ('Classifier', pipeline.learner.get_classifier())
            ],
            feature_names_from='FeatureExtraction'
        )

    raise ValueError('Cannot create ScikitLearn Pipeline for nlp_tool %s' % str(pipeline.nlp_tool))
