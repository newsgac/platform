from collections import OrderedDict

import numpy
from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn.base import TransformerMixin

from newsgac.common.utils import model_to_dict
from newsgac.nlp_tools.models.frog_extract_features import get_frog_features
from newsgac.nlp_tools.models.frog_features import feature_descriptions, features
from newsgac.pipelines.utils import dict_vectorize
from newsgac.tasks.progress import report_progress
from newsgac.nlp_tools.models.nlp_tool import NlpTool


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


class FrogFeatureExtractor(TransformerMixin):
    def __init__(self, nlp_tool):
        self.nlp_tool = nlp_tool

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        articles = X
        extract_features_dict = self.nlp_tool.parameters.features.to_son().to_dict()
        features = []
        for idx, article in enumerate(articles):
            report_progress('frog', float(idx) / len(articles))
            article_features = {
                k: v for k,v in
                get_frog_features(article).iteritems()
                if extract_features_dict[k]
            }
            features.append(OrderedDict(sorted(article_features.items(), key=lambda t: t[0])))

        report_progress('frog', 1)

        # assert each article has the same set of feature keys
        for i in range(len(features) - 1):
            assert features[i].keys() == features[i+1].keys()

        # features is a list of ordered dicts like { [feature_name]: [feature_value] }
        return numpy.array([f.values() for f in features])

    def get_feature_names(self):
        features_dict = model_to_dict(self.nlp_tool.parameters.features)
        return sorted(features_dict.keys())


class Frog(NlpTool):
    name = 'Frog'
    tag = 'frog'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_feature_extractor(self):
        return FrogFeatureExtractor(self)
