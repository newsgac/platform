#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Genre Classifier
#
# Copyright (C) 2016 Juliette Lonij, Koninklijke Bibliotheek -
# National Library of the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from collections import OrderedDict

from sklearn.model_selection import KFold
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import accuracy_score
from src.models.data_sources.data_source_old import DataSource
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedShuffleSplit
from src.data_engineering.postprocessing import Result
from src.database import DATABASE
import numpy as np

# np.random.seed(42)

class CLF():

    def __init__(self, experiment):

        if experiment.type == "SVC":
            # self.class_weight = {1: 0.5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0.9, 7: 0.65, 8: 1}
            self.clf = svm.SVC(kernel=str(experiment.kernel), C=experiment.penalty_parameter_c, decision_function_shape='ovr',
                          # class_weight=self.class_weight,
                               class_weight='balanced',
                               probability=True, random_state=experiment.random_state, gamma=0.1)

        elif experiment.type == "RF":
            self.clf = RandomForestClassifier(n_estimators=experiment.n_estimators, max_features=experiment.max_features,
                                              random_state=experiment.random_state)

        elif experiment.type == "NB":
            self.clf = MultinomialNB(alpha=0.1)

        elif experiment.type == "MLP":
            self.clf = MLPClassifier()

        elif experiment.type == "XGB":
            self.clf = XGBClassifier(max_depth=experiment.max_depth, n_estimators=experiment.n_estimators,
                                     objective= 'multi:softprob', random_state=experiment.random_state,
                                     learning_rate=0.15)

        data_source = DataSource.get_by_id(experiment.data_source_id)
        ds_X_train = DATABASE.load_object(data_source.X_train_handler)
        ds_X_test = DATABASE.load_object(data_source.X_test_handler)
        ds_y_train_with_ids = DATABASE.load_object(data_source.y_train_with_ids_handler)
        ds_y_test_with_ids = DATABASE.load_object(data_source.y_test_with_ids_handler)

        if "tf-idf" not in data_source.pre_processing_config.values():
            # apply feature selection TODO:test this bit

            if experiment.auto_feat:
                self.X_train = np.asarray(ds_X_train)
                self.X_test = np.asarray(ds_X_test)
            else:
                selected_features_index = []
                idx = 0
                for key, val in experiment.features.items():
                    if val:
                        selected_features_index.append(idx)
                    idx += 1
                temp_X_train = []
                temp_X_test = []

                for row in ds_X_train:
                    selected_row = [row[k] for k in selected_features_index]
                    temp_X_train.append(selected_row)

                for row in ds_X_test:
                    selected_row = [row[k] for k in selected_features_index]
                    temp_X_test.append(selected_row)

                self.X_train = np.asarray(temp_X_train)
                self.X_test = np.asarray(temp_X_test)

            # The documents are retrieved in the same order from DB so y values are valid for matching
            self.y_train_with_ids = ds_y_train_with_ids
            self.y_test_with_ids = ds_y_test_with_ids

            self.y_train = np.asarray([row[0] for row in self.y_train_with_ids])
            self.y_test = np.asarray([row[0] for row in self.y_test_with_ids])
        else:
            training_data = []
            testing_data = []
            training_labels = []
            testing_labels = []

            for d in ds_X_train:
                training_data.append(d.strip().encode('utf-8'))
            for d in ds_X_test:
                testing_data.append(d.strip().encode('utf-8'))
            for d in ds_y_train_with_ids:
                training_labels.append(d[0])
            for d in ds_y_test_with_ids:
                testing_labels.append(d[0])

            self.X_train = training_data
            self.X_test = testing_data
            self.y_train = training_labels
            self.y_test = testing_labels


    def train(self):
        trained_model = self.clf.fit(self.X_train, self.y_train)
        return trained_model

    def train_nltk(self, train_vectors_handler):
        vectorizer = DATABASE.load_object(train_vectors_handler)
        trained_model = self.clf.fit(vectorizer, self.y_train)
        return trained_model

    @staticmethod
    def predict(classifier, example):
        return classifier.predict_proba(example)

    def populate_results(self, classifier):
        # y_pred = classifier.predict(self.X_test)
        # cv = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        cv = KFold(n_splits=10, random_state=42, shuffle=True)
        X_all = np.vstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        y_pred = cross_val_predict(estimator=classifier, X=X_all, y=y_all, method='predict', cv=cv)
        results_eval = Result(y_test=y_all, y_pred=y_pred)

        print ("Number of eval samples")
        print len(y_all)
        scores = cross_val_score(classifier, X_all, y_all, cv=cv)
        print("Eval Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        results_eval.accuracy = format(scores.mean(), '.2f')
        results_eval.std = format(scores.std() * 2, '.2f')

        # trained_model results
        y_pred_mod = classifier.predict(self.X_test)
        results_model = Result(y_test=self.y_test, y_pred=y_pred_mod)

        print ("Number of test samples")
        print len(self.y_test)
        # scores = cross_val_score(classifier, self.X_test, self.y_test, cv=cv)
        # print("Test CrossVal Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        acc = accuracy_score(y_true=self.y_test, y_pred=y_pred_mod)
        print("Model Accuracy: %0.4f" % acc)
        # results_model.accuracy = format(scores.mean(), '.2f')
        results_model.accuracy = format(acc, '.2f')

        return results_eval, results_model

    def populate_results_nltk(self, classifier, vectorizer_handler):
        vectorizer = DATABASE.load_object(vectorizer_handler)

        cv = KFold(n_splits=10, random_state=42, shuffle=True)
        X_all = np.hstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        y_pred = cross_val_predict(estimator=classifier, X=vectorizer.transform(X_all), y=y_all, method='predict', cv=cv)
        results_eval = Result(y_test=y_all, y_pred=y_pred)

        print ("Number of eval samples")
        print len(y_all)
        scores = cross_val_score(classifier, vectorizer.transform(X_all), y_all, cv=cv)
        print("Eval Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        results_eval.accuracy = format(scores.mean(), '.2f')

        # trained_model results
        y_pred_mod = classifier.predict(vectorizer.transform(self.X_test))
        results_model = Result(y_test=self.y_test, y_pred=y_pred_mod)

        print ("Number of test samples")
        print len(self.y_test)
        # scores = cross_val_score(classifier, vectorizer.transform(self.X_test), self.y_test, cv=cv)
        # print("Test CrossVal Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        acc = accuracy_score(y_true=self.y_test, y_pred=y_pred_mod)
        print("Model Accuracy: %0.4f" % acc)
        # results_model.accuracy = format(scores.mean(), '.2f')
        results_model.accuracy = format(acc, '.2f')

        return results_eval, results_model
