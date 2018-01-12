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

import src.data_engineering.io as io
from sklearn import svm
from sklearn.model_selection import cross_val_score, StratifiedShuffleSplit
from sklearn.externals import joblib
import dill
from src.common.database import Database

DATABASE = Database()

class SVM_SVC():

    def __init__(self, experiment):
        self.class_weight = {1: 0.5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0.9, 7: 0.65, 8: 1}
        self.clf = svm.SVC(kernel=experiment.kernel, C=experiment.penalty_parameter_c, decision_function_shape='ovr',
                      class_weight=self.class_weight, probability=experiment.probability, random_state=experiment.random_state)

        # Load an existing training set
        self.X_train, self.y_train = io.load_data('training.txt')

    def validate(self):
        # Ten-fold cross-validation with stratified sampling
        cv = StratifiedShuffleSplit(n_splits=10)
        scores = cross_val_score(self.clf, self.X_train, self.y_train, cv=cv)
        print("Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    def train(self):
        trained_model = self.clf.fit(self.X_train, self.y_train)
        return trained_model

    def predict(self, classifier):
        logits = classifier.decision_function([self.X_train[0]])
        print logits
        if self.clf.probability:
            proba = classifier.predict_proba([self.X_train[0]])
            print proba
