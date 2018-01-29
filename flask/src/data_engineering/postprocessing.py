from __future__ import division
import numpy as np
from sklearn.metrics import confusion_matrix
import data_engineering.utils as DataUtils
from sklearn import metrics

__author__ = 'abilgin'

class Result(object):

    def __init__(self, y_test, y_pred):

        self.y_test = y_test
        self.y_pred = y_pred

        self.genre_names = []
        for number, name in DataUtils.genres.items():
            self.genre_names.append(''.join(name))

        self.confusion_matrix = confusion_matrix(self.y_test, self.y_pred)

        self.precision_weighted = format(metrics.precision_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.precision_micro = format(metrics.precision_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.precision_macro = format(metrics.precision_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.recall_weighted =format(metrics.recall_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.recall_micro =format(metrics.recall_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.recall_macro =format(metrics.recall_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.fmeasure_weighted = format(metrics.f1_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.fmeasure_micro = format(metrics.f1_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.fmeasure_macro = format(metrics.f1_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.cohens_kappa = format(metrics.cohen_kappa_score(self.y_test, self.y_pred), '.2f')

        self.accuracy = 0

        np.set_printoptions(precision=2)

    def get_confusion_matrix(self):
        return self.confusion_matrix

    @staticmethod
    def normalise_confusion_matrix(cm):
        return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]