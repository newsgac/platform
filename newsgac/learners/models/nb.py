from pymodm import fields, EmbeddedMongoModel
from sklearn.naive_bayes import MultinomialNB

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    alpha = fields.FloatField(default=0.1)


class LearnerNB(Learner):
    name = 'Naive Bayes'
    tag = 'nb'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_classifier(self):
        return MultinomialNB(alpha=self.parameters.alpha)
