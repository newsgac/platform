import datetime
from collections import OrderedDict

import dill
from sklearn.preprocessing import RobustScaler

from src.data_engineering.preprocessing import Preprocessor, process_raw_text_for_config, get_clean_ocr, \
    remove_stop_words, apply_lemmatization
from src.models.data_sources.data_source import DataSource
from src.machine_learning.clf import CLF
from src.models.configurations.configuration_svc import ConfigurationSVC
from src.models.configurations.configuration_rf import ConfigurationRF
from src.models.configurations.configuration_nb import ConfigurationNB
from src.run import DATABASE
import src.models.experiments.constants as ExperimentConstants
import src.models.data_sources.constants as DataSourceConstants
import src.common.utils as Utilities
import src.data_engineering.utils as DataUtilities
from src.models.users.user import User
import numpy as np


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
            self.results_eval_handler = None
            self.results_model_handler = None
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
    def get_finished_user_experiments(cls, user_email):
        return [cls(**elem) for elem in
                DATABASE.find(ExperimentConstants.COLLECTION, {"user_email": user_email, "run_finished": {"$ne": None}})]

    @classmethod
    def get_finished_user_experiments_using_data_id(cls, user_email, ds_id):
        return [cls(**elem) for elem in DATABASE.find(ExperimentConstants.COLLECTION,
                              {"user_email": user_email, "data_source_id": ds_id, "run_finished": {"$ne": None}})]

    @classmethod
    def get_any_user_experiments_using_data_id(cls, user_email, ds_id):
        return [cls(**elem) for elem in DATABASE.find(ExperimentConstants.COLLECTION,
                                                      {"user_email": user_email, "data_source_id": ds_id})]

    @classmethod
    def get_public_experiments_using_data_id(cls, ds_id):
        return [cls(**elem) for elem in DATABASE.find(ExperimentConstants.COLLECTION,
                                                      {"public_flag": True, "data_source_id": ds_id,
                                                       "run_finished": {"$ne": None}})]

    @staticmethod
    def get_used_data_sources_for_user(user_email):
        return DATABASE.find(ExperimentConstants.COLLECTION, {"user_email": user_email}).distinct("data_source_id")

    @staticmethod
    def get_used_data_sources_for_public():
        return DATABASE.find(ExperimentConstants.COLLECTION, {"public_flag": True}).distinct("data_source_id")

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

    def get_results_eval(self):
        pickled_results = DATABASE.getGridFS().get(self.results_eval_handler).read()
        return dill.loads(pickled_results)

    def get_results_model(self):
        pickled_results = DATABASE.getGridFS().get(self.results_model_handler).read()
        return dill.loads(pickled_results)

    def predict(self, raw_text, ds):
        # TODO: test this bit
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)
        sorted_resp = {}
        preprocessor = Preprocessor(ds.pre_processing_config)

        if 'tf-idf' in ds.pre_processing_config.values():
            #NLTK case
            pickled_model = DATABASE.getGridFS().get(ds.vectorizer_handler).read()
            vectorizer = dill.loads(pickled_model)

            clean_ocr = get_clean_ocr(raw_text.lower())

            if 'sw_removal' in ds.pre_processing_config.keys():
                clean_ocr = remove_stop_words(clean_ocr)
            if 'lemmatization' in ds.pre_processing_config.keys():
                clean_ocr = apply_lemmatization(clean_ocr)

            tfidf_vectors = vectorizer.transform([clean_ocr])
            proba = CLF.predict(classifier, tfidf_vectors)
        else:
            processed_text, feats, id = process_raw_text_for_config(preprocessor, raw_text)
            sorted_keys = sorted(self.features.keys())
            ordered_feature_values = [feats[f] for f in sorted_keys if
                                      f not in DataSourceConstants.NON_FEATURE_COLUMNS]
            if 'scaling' in ds.pre_processing_config.keys():
                scaler = dill.loads(DATABASE.getGridFS().get(ds.scaler_handler).read())
                if  not self.auto_feat:
                    # ugly solution but will refactor later
                    # descale and scale again
                    # revert the data back to original
                    training_data = np.array(dill.loads(DATABASE.getGridFS().get(ds.X_train_handler).read()))
                    original_training_data = scaler.inverse_transform(training_data)
                    indexes = []
                    for i, f in enumerate(sorted(feats.keys()), 0):
                        if f in sorted_keys:
                            indexes.append(i)

                    selected_training_data = original_training_data[:, sorted(indexes)]
                    scaler = RobustScaler().fit(selected_training_data)

                feature_set = scaler.transform([ordered_feature_values])
            else:
                feature_set = [ordered_feature_values]
            proba = CLF.predict(classifier, feature_set)

        probabilities = proba[0].tolist()

        resp = {}
        for i, p in enumerate(probabilities):
            resp[DataUtilities.genres[i + 1][0].split('/')[0]] = format(p, '.2f')

        sorted_resp = OrderedDict(sorted(resp.items(), key=lambda t: t[1], reverse=True))

        return sorted_resp

    def get_classifier(self):
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)
        return classifier

    def populate_hypothesis_df(self, exp_data_source, hypotheses_data_source):
        data = {}
        articles = hypotheses_data_source.get_test_instances()
        count1985 = 0
        count1965 = 0
        import pandas as pd
        for article in articles:
            # year extraction
            if 'date' not in article.keys():
                break
            date_from_db = article['date'].split("-")[2]
            if date_from_db not in data.keys():
                data[date_from_db] = {}

            prediction = (self.predict(article['article_raw_text'], exp_data_source)).keys()[0]
            if prediction not in data[date_from_db].keys():
                data[date_from_db][prediction] = 0
            data[date_from_db][prediction] += 1
            if date_from_db == "1985":
                count1985 += 1
            elif date_from_db == "1965":
                count1965 += 1

        normalised_data = {}
        for date in data:
            normalised_data[date] = {}
            for genre in data[date]:
                # normalised_data[date][genre] = (round( data[date][genre] * 100 / len(articles), 2))
                if date == "1985":
                    normalised_data[date][genre] = (round(data[date][genre] * 100 / count1985, 2))
                else:
                    normalised_data[date][genre] = (round(data[date][genre] * 100 / count1965, 2))

        df = pd.DataFrame(normalised_data, columns=data.keys())
        df.fillna(0, inplace=True)

        return df


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
        DATABASE.getGridFS().delete(self.trained_model_handler)
        DATABASE.getGridFS().delete(self.results_eval_handler)
        DATABASE.getGridFS().delete(self.results_model_handler)
        ConfigurationSVC.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})

    def run_svc(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        ds = DataSource.get_by_id(self.data_source_id)
        # train
        svc = CLF(self)

        if "tf-idf" not in ds.pre_processing_config.values():
            trained_model = svc.train()
            # populate results
            results_eval, results_model = svc.populate_results(trained_model)
        else:
            trained_model = svc.train_nltk(ds.train_vectors_handler)
            # populate results
            results_eval, results_model = svc.populate_results_nltk(trained_model, ds.vectorizer_handler)

        self.trained_model_handler = DATABASE.getGridFS().put(dill.dumps(trained_model))
        self.results_eval_handler = DATABASE.getGridFS().put(dill.dumps(results_eval))
        self.results_model_handler = DATABASE.getGridFS().put(dill.dumps(results_model))

        # update the timestamp
        self.run_finished = datetime.datetime.utcnow()
        self.save_to_db()

    def get_features_weights(self):
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)
        feature_weights = None

        # check if kernel is linear
        if self.kernel == 'linear':
            feature_weights = classifier.coef_

        return feature_weights


class ExperimentRF(Experiment, ConfigurationRF):

    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationRF.__init__(self, user_email, **kwargs)
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
        DATABASE.getGridFS().delete(self.trained_model_handler)
        DATABASE.getGridFS().delete(self.results_eval_handler)
        DATABASE.getGridFS().delete(self.results_model_handler)
        ConfigurationRF.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})

    def run_rf(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        ds = DataSource.get_by_id(self.data_source_id)
        # train
        rf = CLF(self)

        if "tf-idf" not in ds.pre_processing_config.values():
            trained_model = rf.train()
            # populate results
            results_eval, results_model = rf.populate_results(trained_model)
        else:
            trained_model = rf.train_nltk(ds.train_vectors_handler)
            # populate results
            results_eval, results_model = rf.populate_results_nltk(trained_model, ds.vectorizer_handler)

        self.trained_model_handler = DATABASE.getGridFS().put(dill.dumps(trained_model))
        self.results_eval_handler = DATABASE.getGridFS().put(dill.dumps(results_eval))
        self.results_model_handler = DATABASE.getGridFS().put(dill.dumps(results_model))

        # update the timestamp
        self.run_finished = datetime.datetime.utcnow()
        self.save_to_db()


class ExperimentNB(Experiment, ConfigurationNB):

    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationNB.__init__(self, user_email, **kwargs)
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
        DATABASE.getGridFS().delete(self.trained_model_handler)
        DATABASE.getGridFS().delete(self.results_eval_handler)
        DATABASE.getGridFS().delete(self.results_model_handler)
        ConfigurationNB.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})

    def run_nb(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        ds = DataSource.get_by_id(self.data_source_id)
        # train
        nb = CLF(self)

        if "tf-idf" not in ds.pre_processing_config.values():
            trained_model = nb.train()
            # populate results
            results_eval, results_model = nb.populate_results(trained_model)
        else:
            trained_model = nb.train_nltk(ds.train_vectors_handler)
            # populate results
            results_eval, results_model = nb.populate_results_nltk(trained_model, ds.vectorizer_handler)

        self.trained_model_handler = DATABASE.getGridFS().put(dill.dumps(trained_model))
        self.results_eval_handler = DATABASE.getGridFS().put(dill.dumps(results_eval))
        self.results_model_handler = DATABASE.getGridFS().put(dill.dumps(results_model))

        # update the timestamp
        self.run_finished = datetime.datetime.utcnow()
        self.save_to_db()

    def get_features_weights(self):
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)
        return classifier.coef_
