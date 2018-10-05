from nltk import sent_tokenize
from pymodm import EmbeddedMongoModel
from pymodm import fields
from pynlpl.clients.frogclient import FrogClient

import config
from common.utils import split_chunks, split_long_sentences
from nlp_tools.models.frog_extract_features import get_frog_features
from nlp_tools.models.frog_features import feature_descriptions, features
from .nlp_tool import NlpTool


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


class Frog(NlpTool):
    name = 'Frog'
    tag = 'frog'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_features(self, text):
        return {k: v for k,v in get_frog_features(text).iteritems() if self.parameters.features.to_son().to_dict()[k]}


