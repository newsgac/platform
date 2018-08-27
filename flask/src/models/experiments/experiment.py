import datetime
import uuid
from collections import OrderedDict

from sklearn.preprocessing import RobustScaler

from src.data_engineering.preprocessing import Preprocessor, process_raw_text_for_config, get_clean_ocr, \
    remove_stop_words, apply_lemmatization
from src.machine_learning.clf import CLF
from src.database import DATABASE
import src.models.experiments.constants as ExperimentConstants
import src.models.data_sources.constants as DataSourceConstants
import src.common.utils as Utilities
import src.data_engineering.utils as DataUtilities

from src.models.users.user import User
import numpy as np
import pandas as pd

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
        return DATABASE.load_object(self.results_eval_handler)

    def get_results_model(self):
        return DATABASE.load_object(self.results_model_handler)

    def predict(self, raw_text, ds):
        # TODO: test this bit
        classifier = DATABASE.load_object(self.trained_model_handler)
        sorted_resp = {}
        preprocessor = Preprocessor(ds.pre_processing_config)

        if 'tf-idf' in ds.pre_processing_config.values():
            #NLTK case
            vectorizer = DATABASE.load_object(ds.vectorizer_handler)

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
                scaler = DATABASE.load_object(ds.scaler_handler)
                if  not self.auto_feat:
                    # ugly solution but will refactor later
                    # descale and scale again
                    # revert the data back to original
                    training_data = np.array(DATABASE.load_object(ds.X_train_handler).read())
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
        return DATABASE.load_object(self.trained_model_handler)

    def populate_hypothesis_df(self, exp_data_source, hypotheses_data_source):
        from src.visualisation.comparison import ExperimentComparator
        data = {}
        articles = hypotheses_data_source.get_test_instances()
        count1985 = 0
        count1965 = 0

        # adding features to unlabelled data
        preproc = Preprocessor(exp_data_source.pre_processing_config)
        art_ids, feat_mat = preproc.do_parallel_processing_matrix(articles)
        hypotheses_data_source.add_features_to_db_real_data(exp_data_source._id, art_ids, feat_mat)

        for article in articles:
            # year extraction
            if 'date' not in article.keys() or article['date'] is None:
                break
            date_from_db = article['date'].split("-")[2]
            if date_from_db not in data.keys():
                data[date_from_db] = {}

            existing_pred = ExperimentComparator.get_existing_article_predictions(article_text=article['article_raw_text'])

            if existing_pred is None:
                ExperimentComparator.save_article_comparison(id=uuid.uuid4().hex, article_text=article['article_raw_text'], ds_id=exp_data_source._id)
                prediction = (self.predict(article['article_raw_text'], exp_data_source)).keys()[0]
                ExperimentComparator.update_article_comparison_by_experiment(article_text=article['article_raw_text'],
                                                             exp_id=self._id, prediction=prediction)
            elif self._id not in existing_pred["exp_predictions"].keys():
                prediction = (self.predict(article['article_raw_text'], exp_data_source)).keys()[0]
                ExperimentComparator.update_article_comparison_by_experiment(article_text=article['article_raw_text'],
                                                             exp_id=self._id, prediction=prediction)
            else:
                prediction = existing_pred["exp_predictions"][self._id]

            if prediction not in data[date_from_db].keys():
                data[date_from_db][prediction] = 0
            data[date_from_db][prediction] += 1
            if date_from_db == "1985":
                count1985 += 1
            elif date_from_db == "1965":
                count1965 += 1

        # TODO: add bias correction using misclassification method from Emma's paper

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


