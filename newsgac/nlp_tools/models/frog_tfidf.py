from pymodm import fields
from newsgac.nlp_tools.models.frog import Parameters
from newsgac.nlp_tools.models.nlp_tool import NlpTool

class FrogTFIDF(NlpTool):
    name = 'Frog + TFIDF'
    tag = 'frog_tfidf'
    parameters = fields.EmbeddedDocumentField(Parameters)
