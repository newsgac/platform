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

from src.models.data_sources.data_source import DataSource
import src.models.data_sources.constants as DataSourceConstants
from sklearn import svm
from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedShuffleSplit
from src.data_engineering.postprocessing import Result
from src.run import DATABASE
import numpy as np
import dill

# np.random.seed(42)

class SVM_SVC():

    def __init__(self, experiment):
        # self.class_weight = {1: 0.5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0.9, 7: 0.65, 8: 1}
        self.clf = svm.SVC(kernel=str(experiment.kernel), C=experiment.penalty_parameter_c, decision_function_shape='ovr',
                      # class_weight=self.class_weight,
                           probability=True, random_state=experiment.random_state)

        if experiment.kernel == 'linear':
            self.feature_weights = []
        else:
            self.feature_weights = None

        data_source = DataSource.get_by_id(experiment.data_source_id)
        ds_X_train = dill.loads(DATABASE.getGridFS().get(data_source.X_train_handler).read())
        ds_X_test = dill.loads(DATABASE.getGridFS().get(data_source.X_test_handler).read())
        ds_y_train_with_ids = dill.loads(DATABASE.getGridFS().get(data_source.y_train_with_ids_handler).read())
        ds_y_test_with_ids = dill.loads(DATABASE.getGridFS().get(data_source.y_test_with_ids_handler).read())

        if "nltk" not in data_source.pre_processing_config.values():
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

        # mean_scores = np.array(grid.cv_results_['mean_test_score'])
        # # scores are in the order of param_grid iteration, which is alphabetical
        # mean_scores = mean_scores.reshape(len(C_OPTIONS), -1, len(N_FEATURES_OPTIONS))
        # # select score for best C
        # mean_scores = mean_scores.max(axis=0)
        # bar_offsets = (np.arange(len(N_FEATURES_OPTIONS)) *
        #                (len(reducer_labels) + 1) + .5)
        #
        # plt.figure()
        # COLORS = 'bgrcmyk'
        # for i, (label, reducer_scores) in enumerate(zip(reducer_labels, mean_scores)):
        #     plt.bar(bar_offsets + i, reducer_scores, label=label, color=COLORS[i])
        #
        # plt.title("Comparing feature reduction techniques")
        # plt.xlabel('Reduced number of features')
        # plt.xticks(bar_offsets + len(reducer_labels) / 2, N_FEATURES_OPTIONS)
        # plt.ylabel('Digit classification accuracy')
        # plt.ylim((0, 1))
        # plt.legend(loc='upper left')

    def cross_validate(self):
        # Ten-fold cross-validation with stratified sampling
        cv = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        X_all = np.vstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        scores = cross_val_score(self.clf, X_all, y_all, cv=cv)
        print("Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores

    def cross_validate_nltk(self, vectorizer):
        # Ten-fold cross-validation with stratified sampling
        cv = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        X_all = np.hstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        scores = cross_val_score(self.clf, vectorizer.transform(X_all), y_all, cv=cv)
        print("Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores

    def train(self):
        trained_model = self.clf.fit(self.X_train, self.y_train)
        return trained_model

    def train_nltk(self, train_vectors_handler):
        pickled_model = DATABASE.getGridFS().get(train_vectors_handler).read()
        vectorizer = dill.loads(pickled_model)
        trained_model = self.clf.fit(vectorizer, self.y_train)
        return trained_model

    @staticmethod
    def get_feature_weights(classifier):
        return classifier.coef_

    @staticmethod
    def predict(classifier, example):
        # return classifier.predict_proba(example)
        cv = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        return cross_val_predict(classifier, example, method='predict_proba')


    def populate_results(self, classifier):
        # y_pred = classifier.predict(self.X_test)
        # cv = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        cv = KFold(n_splits=10, random_state=42, shuffle=True)
        X_all = np.vstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        y_pred = cross_val_predict(estimator=classifier, X=X_all, y=y_all, method='predict', cv=cv)
        results = Result(y_test=y_all, y_pred=y_pred)
        print ("Number of samples")
        print len(y_all)
        scores = self.cross_validate()
        results.accuracy = format(scores.mean(), '.2f')
        return results

    def populate_results_nltk(self, classifier, vectorizer_handler):
        pickled_model = DATABASE.getGridFS().get(vectorizer_handler).read()
        vectorizer = dill.loads(pickled_model)
        # y_pred = classifier.predict(vectorizer.transform(self.X_test))
        # cv = ShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
        cv = KFold(n_splits=10, random_state=42, shuffle=True)
        X_all = np.hstack((self.X_train, self.X_test))
        y_all = np.hstack((self.y_train, self.y_test))
        y_pred = cross_val_predict(estimator=classifier, X=vectorizer.transform(X_all),
                                   y=y_all, method='predict', cv=cv)
        results = Result(y_test=y_all, y_pred=y_pred)
        print ("Number of samples")
        print len(y_all)
        scores = self.cross_validate_nltk(vectorizer)
        results.accuracy = format(scores.mean(), '.2f')
        return results


