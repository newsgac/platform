from pymodm import fields, EmbeddedMongoModel

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    default_alpha = fields.FloatField(default=0.1)


class LearnerNB(Learner):
    name = 'Naive Bayes'
    tag = 'nb'
    parameters = fields.EmbeddedDocumentField(Parameters)

