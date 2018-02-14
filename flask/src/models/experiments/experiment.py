import datetime
from collections import OrderedDict

import dill

from data_engineering.feature_extraction import Article
from machine_learning.svm import SVM_SVC
from models.configurations.configuration_svc import ConfigurationSVC
from src.common.database import Database
import src.models.experiments.constants as ExperimentConstants
import src.common.utils as Utilities
import src.data_engineering.utils as DataUtilities
from src.models.configurations.configuration_dt import ConfigurationDT
from src.models.users.user import User
import sklearn

DATABASE = Database()
UT = Utilities.Utils()

__author__ = 'abilgin'

class Experiment(object):

    def __init__(self, user_email, display_title, public_flag, **kwargs):

        if 'configuration' in kwargs:
            # creation from the web
            self.created = datetime.datetime.utcnow()
            self.run_started = None
            self.run_finished = None
            self.trained_model_handler = None
            self.results_handler = None
        else:
            # default constructor from the database
            self.__dict__.update(kwargs)

        self.user_email = user_email
        self.display_title = display_title
        self.public_flag = public_flag

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(ExperimentConstants.COLLECTION, {"_id": id}))

    @classmethod
    def get_by_title(cls, title):
        return cls(**DATABASE.find_one(ExperimentConstants.COLLECTION, {"display_title": title}))

    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(ExperimentConstants.COLLECTION, {"user_email": user_email})]

    @classmethod
    def get_public_experiments(cls):
        return [cls(**elem) for elem in DATABASE.find(ExperimentConstants.COLLECTION, {"public_flag": True, "run_finished": {"$ne" : None}})]

    @classmethod
    def get_finished_experiments(cls):
        return [cls(**elem) for elem in
                DATABASE.find(ExperimentConstants.COLLECTION, {"": True, "run_finished": {"$ne": None}})]

    def get_public_username(self):
        return User.get_by_email(self.user_email).username

    def get_user_friendly_created(self):
        return UT.get_local_display_time(self.created)

    def get_user_friendly_run_started(self):
        if self.run_started is not None:
            return UT.get_local_display_time(self.run_started)
        return None

    def get_user_friendly_run_finished(self):
        if self.run_finished is not None:
            return UT.get_local_display_time(self.run_finished)
        return None

    def get_run_duration(self):
        delta = self.run_finished - self.run_started
        m, s = divmod(delta.seconds, 60)
        h, m = divmod(m, 60)
        if int(h) == 0:
            return "{:2d} minutes {:2d} seconds".format(int(m), int(s))

        return "{:2d} hours {:2d} minutes {:2d} seconds".format(int(h), int(m), int(s))

    def get_results(self):
        print self.results_handler
        pickled_results = DATABASE.getGridFS().get(self.results_handler).read()
        return dill.loads(pickled_results)

    def predict(self, raw_text):
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)
        sorted_resp = {}

        if type(classifier) is sklearn.svm.classes.SVC:
            svc = SVM_SVC(self)
            # convert raw text to structured example
            example = Article.convert_raw_to_features(raw_text)
            proba = svc.predict(classifier, example)
            probabilities = proba[0].tolist()

            resp = {}
            for i, p in enumerate(probabilities):
                resp[DataUtilities.genres[i + 1][0].split('/')[0]] = format(p, '.2f')

            sorted_resp = OrderedDict(sorted(resp.items(), key=lambda t: t[1], reverse=False))

        return sorted_resp

class ExperimentDT(Experiment, ConfigurationDT):

    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationDT.__init__(self, user_email, **kwargs)
        Experiment.__init__(self, user_email, display_title, public_flag, **kwargs)

    def __repr__(self):
        return "<Experiment {}>".format(self.display_title)

    def save_to_db(self):
        DATABASE.update(ExperimentConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def delete(self):
        id = self._id
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})
        ConfigurationDT.delete(self)

    def start_running(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        # TODO: under construction

        # call the training method


        # self.run_finished = datetime.datetime.utcnow()
        # self.save_to_db()


class ExperimentSVC(Experiment, ConfigurationSVC):

    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationSVC.__init__(self, user_email, **kwargs)
        Experiment.__init__(self, user_email, display_title, public_flag, **kwargs)

    def __repr__(self):
        return "<Experiment {}>".format(self.display_title)

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(ExperimentConstants.COLLECTION, {"_id": id}))

    def save_to_db(self):
        DATABASE.update(ExperimentConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def delete(self):
        id = self._id
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})
        ConfigurationSVC.delete(self)
        DATABASE.getGridFS().delete(self.trained_model_handler)
        DATABASE.getGridFS().delete(self.results_handler)

    def start_running(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        # train
        svc = SVM_SVC(self)
        trained_model = svc.train()
        self.trained_model_handler = DATABASE.getGridFS().put(dill.dumps(trained_model))

        self.run_finished = datetime.datetime.utcnow()

        # populate results
        results = svc.populate_results(trained_model)
        self.results_handler = DATABASE.getGridFS().put(dill.dumps(results))
        self.save_to_db()



