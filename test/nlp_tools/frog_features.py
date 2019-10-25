import numpy
import pytest
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from newsgac.nlp_tools import Frog


@pytest.mark.frog
def test_frog_features():
    text = 'Dit is een willekeurige tekst waar wat frog features uitgehaald worden. Dit is de tweede zin.'
    frog = Frog.create()

    pipeline = Pipeline([
        ('Frog', frog),
        ('DictVectorizer', DictVectorizer()),
    ])

    expected_features = numpy.array(['adjectives_perc', 'cogn_verbs_perc', 'intensifiers_perc', 'modal_adverbs_perc', 'modal_verbs_perc', 'named_entities_perc', 'pronoun_1_perc', 'pronoun_2_perc', 'pronoun_3_perc', 'unique_named_entities'])

    result = pipeline.fit_transform([text])

    if not result.shape == (1, len(expected_features)): raise AssertionError()
    if not (pipeline.steps[1][1].get_feature_names() == expected_features).all(): raise AssertionError()
