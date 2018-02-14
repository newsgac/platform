from __future__ import division

from collections import OrderedDict

import numpy as np
from sklearn.metrics import confusion_matrix
import src.data_engineering.utils as DataUtils
from sklearn import metrics

from src.data_engineering.feature_extraction import Article

__author__ = 'abilgin'

class Result(object):

    def __init__(self, y_test, y_pred):

        self.y_test = y_test
        self.y_pred = y_pred

        self.genre_names = []
        for number, name in DataUtils.genres.items():
            self.genre_names.append(''.join(name).split('/')[0])

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

    @staticmethod
    def predict_raw_example(experiment, text=None, url=None):

        if text:
            art = Article(text=text)
        elif url:
            art = Article(url=url)
        else:
            return {}

        example = [art.features[f] for f in DataUtils.features] #TODO: change to DB
        print example

        # experiment = Experiment.get_by_id("312a051d991e4b16ae7042ed27428ecb")
        # experiment = Experiment.get_by_id("6e5220a1e1f942c884ebe0cf82817182")

        proba = experiment.predict([example])
        probabilities = proba[0].tolist()

        resp = {}
        for i, p in enumerate(probabilities):
            resp[DataUtils.genres[i + 1][0].split('/')[0]] = p

        sorted_resp = OrderedDict(sorted(resp.items(), key=lambda t: t[1], reverse=True))
        print sorted_resp

        return sorted_resp