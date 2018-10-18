from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn.feature_extraction.text import TfidfVectorizer

from .nlp_tool import NlpTool


class Parameters(EmbeddedMongoModel):
    scaling = fields.BooleanField(required=True, default=True)
    scaling.description = 'Transforms features by using statistics that are robust to outliers.'


class TFIDF(NlpTool):
    name = 'TF-IDF'
    tag = 'tfidf'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_feature_extractor(self):
        return TfidfVectorizer(
            sublinear_tf=True,
            min_df=5,
            norm='l2',
            ngram_range=(1, 2)
        )
