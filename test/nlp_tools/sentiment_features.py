import numpy
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from newsgac.nlp_tools.transformers import ExtractSentimentFeatures


def test_sentiment_features():
    text = 'Dit is een willekeurige tekst waar wat sentiment features uitgehaald worden. Dit is de tweede zin.'

    pipeline = Pipeline([
        ('ExtractSentimentFeatures', ExtractSentimentFeatures()),
        ('DictVectorizer', DictVectorizer()),
    ])

    expected_features = numpy.array(['polarity', 'subjectivity'])

    result = pipeline.fit_transform([text])

    assert result.shape == (1, 2)
    assert (pipeline.steps[1][1].get_feature_names() == expected_features).all()
