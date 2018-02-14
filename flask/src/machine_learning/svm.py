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

import src.data_engineering.data_io as io
from sklearn import svm, metrics
from sklearn.model_selection import cross_val_score, StratifiedShuffleSplit, train_test_split

from src.data_engineering.postprocessing import Result
from src.common.database import Database

DATABASE = Database()

class SVM_SVC():

    def __init__(self, experiment):
        self.class_weight = {1: 0.5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0.9, 7: 0.65, 8: 1}
        self.clf = svm.SVC(kernel=str(experiment.kernel), C=experiment.penalty_parameter_c, decision_function_shape='ovr',
                      class_weight=self.class_weight, probability=True, random_state=experiment.random_state)

        # Load an existing training set
        if experiment.data_source_id is None:
            X, y = io.load_preprocessed_data_from_file('training.txt')
        else:
            #read from db
            X, y = io.load_preprocessed_data_from_db(experiment.data_source_id)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, random_state=0)


    def cross_validate(self):
        # Ten-fold cross-validation with stratified sampling
        cv = StratifiedShuffleSplit(n_splits=10)
        scores = cross_val_score(self.clf, self.X_train, self.y_train, cv=cv)
        print("Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores

    def train(self):
        trained_model = self.clf.fit(self.X_train, self.y_train)
        return trained_model

    @staticmethod
    def predict(classifier, example):
        return classifier.predict_proba(example)

    def populate_results(self, classifier):
        y_pred = classifier.predict(self.X_test)
        results = Result(y_test=self.y_test, y_pred=y_pred)
        print ("Number of samples")
        print len(self.y_test)
        scores = self.cross_validate()
        results.accuracy = format(scores.mean(), '.2f')
        return results