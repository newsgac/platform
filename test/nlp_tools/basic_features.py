import numpy
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from newsgac.nlp_tools.transformers import ExtractBasicFeatures


def test_basic_features():
    text = 'Dit is een willekeurige tekst waar wat basic features uitgehaald worden. Dit is de tweede zin.'

    pipeline = Pipeline([
        ('ExtractBasicFeatures', ExtractBasicFeatures()),
        ('DictVectorizer', DictVectorizer()),
    ])

    expected_features = numpy.array(['avg_sentence_length', 'currency_symbols_perc', 'digits_perc', 'exclamation_marks_perc', 'question_marks_perc', 'sentences'])
    expected_result = numpy.array([9, 0, 0, 0, 0, 2])

    result = pipeline.fit_transform([text])
    if not (pipeline.steps[1][1].get_feature_names() == expected_features).all(): raise AssertionError()
    if not (result.todense()[0] == expected_result).all(): raise AssertionError()
