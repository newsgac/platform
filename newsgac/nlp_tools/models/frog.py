from collections import OrderedDict

import numpy
from celery import group, current_task
from celery.result import allow_join_result

from pymodm import EmbeddedMongoModel
from pymodm import fields
from pymodm.errors import DoesNotExist
from sklearn.base import TransformerMixin

from newsgac.caches import Cache
from newsgac.common.utils import model_to_dict, hash_text
from newsgac.nlp_tools.models.frog_extract_features import get_frog_features
from newsgac.nlp_tools.models.frog_features import feature_descriptions, features
from newsgac.nlp_tools.models.nlp_tool import NlpTool
from newsgac.nlp_tools.tasks import frog_process


class Features(EmbeddedMongoModel):
    # adds all features (from array + descr dict) to the Feature class as BooleanFields.
    # todo: there must be a cleaner way to accomplish this
    for feature in features:
        field = fields.BooleanField(blank=True, required=False, default=True)
        field.description = feature_descriptions[feature]
        locals()[feature] = field
    del locals()['field']
    del locals()['feature']


class Parameters(EmbeddedMongoModel):
    parameter_field_name = 'features'

    scaling = fields.BooleanField(required=True, default=True)
    scaling.description = 'Transforms features by using statistics that are robust to outliers.'

    features = fields.EmbeddedDocumentField(Features, default=Features(**{
        field.attname: field.default for field in Features._mongometa.get_fields()
    }))
    features.description = 'Included features.'


# splits a list into equal chunks of size n
def chunk_list(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def populate_frog_cache(texts, max_chunk_size=100):
    uncached = []
    for text in texts:
        try:
            Cache.objects.raw({'hash': hash_text(text)})[0]
        except DoesNotExist:
            uncached.append(text)

    if len(uncached) > 0:
        print(str(len(uncached)) + ' texts to FROG')
        chunks = list(chunk_list(uncached, max_chunk_size))
        with allow_join_result():
            # list of frog tokens per text
            # concurrently process each chunk with celery. Why not chunk_size == 1? Celery has a memory leak,
            # which scales per task, so larger chunks reduce memory leakage.
            print('frogging ' + str(len(chunks)) + ' chunks')
            # waits till done
            group(frog_process.s(chunk) for chunk in chunks)().get()
            print('frogging done')


class FrogFeatureExtractor(TransformerMixin):
    def __init__(self, nlp_tool):
        # we need to know the nlp_tools parameters
        self.nlp_tool = nlp_tool

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print('Frog: ' + str(len(X)) + ' articles')

        texts = X
        populate_frog_cache(texts)
        frog_tokens = [Cache.objects.raw({'hash': hash_text(text)})[0].data.get() for text in texts]
        extract_features_dict = self.nlp_tool.parameters.features.to_son().to_dict()

        features = []
        for article_key, tokens in enumerate(frog_tokens):
            article_features = {
                k: v for k, v in
                get_frog_features(tokens, X[article_key]).iteritems()
                if extract_features_dict[k]
            }
            features.append(OrderedDict(sorted(article_features.items(), key=lambda t: t[0])))

        # assert each article has the same set of feature keys
        for i in range(len(features) - 1):
            if not features[i].keys() == features[i+1].keys(): raise AssertionError()

        # features is a list of ordered dicts like { [feature_name]: [feature_value] }
        return_value = numpy.array([f.values() for f in features])
        return return_value

    def get_feature_names(self):
        features_dict = model_to_dict(self.nlp_tool.parameters.features)
        return sorted(features_dict.keys())


class Frog(NlpTool):
    name = 'Frog'
    tag = 'frog'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_feature_extractor(self):
        return FrogFeatureExtractor(self)
