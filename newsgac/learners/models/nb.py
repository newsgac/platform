from pymodm import fields, EmbeddedMongoModel
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    alpha = fields.FloatField(default=0.1)


class LearnerNB(Learner):
    name = 'Naive Bayes'
    tag = 'nb'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def fit(self, features, labels):
        self.trained_model = MultinomialNB(alpha=self.parameters.alpha)
        self.trained_model.fit(features, labels)
