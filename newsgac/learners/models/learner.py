import numpy
import numpy as np
from pymodm import fields, EmbeddedMongoModel
from sklearn import metrics
from sklearn.metrics import confusion_matrix

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import ParametersMixin
from pipelines.data_engineering import utils as DataUtils


class Result(EmbeddedMongoModel):
    accuracy = fields.FloatField()
    cohens_kappa = fields.FloatField()
    confusion_matrix = ObjectField()
    fmeasure_macro = fields.FloatField()
    fmeasure_micro = fields.FloatField()
    fmeasure_weighted = fields.FloatField()
    precision_macro = fields.FloatField()
    precision_micro = fields.FloatField()
    precision_weighted = fields.FloatField()
    recall_macro = fields.FloatField()
    recall_micro = fields.FloatField()
    recall_weighted = fields.FloatField()
    std = fields.FloatField()
    
    @classmethod
    def from_prediction(cls, true_labels, predicted_labels):
        scores = numpy.array([
            1 if true_labels[i] == predicted_labels[i] else 0 for i in range(0, len(true_labels))
        ])

        return cls(
            confusion_matrix = confusion_matrix(true_labels, predicted_labels, labels=DataUtils.genre_codes),
            precision_weighted = metrics.precision_score(true_labels, predicted_labels, average='weighted'),
            precision_micro = metrics.precision_score(true_labels, predicted_labels, average='micro'),
            precision_macro = metrics.precision_score(true_labels, predicted_labels, average='macro'),
            recall_weighted = metrics.recall_score(true_labels, predicted_labels, average='weighted'),
            recall_micro = metrics.recall_score(true_labels, predicted_labels, average='micro'),
            recall_macro = metrics.recall_score(true_labels, predicted_labels, average='macro'),
            fmeasure_weighted = metrics.f1_score(true_labels, predicted_labels, average='weighted'),
            fmeasure_micro = metrics.f1_score(true_labels, predicted_labels, average='micro'),
            fmeasure_macro = metrics.f1_score(true_labels, predicted_labels, average='macro'),
            cohens_kappa = metrics.cohen_kappa_score(true_labels, predicted_labels),
            accuracy=scores.mean(),
            std=scores.std()
        )


class Learner(ParametersMixin, EmbeddedMongoModel):
    _tag = fields.CharField(required=True)
    trained_model = ObjectField()
    result = fields.EmbeddedDocumentField(Result)
    # def save(self, **kwargs):
    #     self._tag = self.__class__.tag
    #     super(Learner, self).save(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        model.set_default_parameters()
        model._tag = cls.tag
        return model

    #
    # @staticmethod
    # def normalise_confusion_matrix(cm):
    #     sum = cm.sum(axis=1)[:, np.newaxis]
    #     temp = cm.astype('float')
    #     # return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    #     return np.divide(temp, sum, out=np.zeros_like(temp), where=sum!=0)
