from pymodm import EmbeddedMongoModel
from pymodm import fields

from .nlp_tool import NlpTool


class Parameters(EmbeddedMongoModel):
    pass


class TFIDF(NlpTool):
    name = 'TF-IDF'
    tag = 'tfidf'
    parameters = fields.EmbeddedDocumentField(Parameters)
