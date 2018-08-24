import datetime
from collections import OrderedDict

import dill
import pandas as pd

from src.database import DATABASE
from src.machine_learning.clf import CLF
from src.models.configurations.configuration_xgb import ConfigurationXGB
from src.models.data_sources.data_source import DataSource
from src.models.experiments import constants as ExperimentConstants
from src.models.experiments.experiment import Experiment


class ExperimentXGB(Experiment, ConfigurationXGB):
    type = 'XGB'
    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationXGB.__init__(self, user_email, **kwargs)
        Experiment.__init__(self, user_email, display_title, public_flag, **kwargs)

    def __repr__(self):
        return "<Experiment {}>".format(self.display_title)

    def save_to_db(self):
        DATABASE.update(ExperimentConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def delete(self):
        id = self._id
        DATABASE.getGridFS().delete(self.trained_model_handler)
        DATABASE.getGridFS().delete(self.results_eval_handler)
        DATABASE.getGridFS().delete(self.results_model_handler)
        ConfigurationXGB.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})

    def run(self):
        self.run_xgb()

    def run_xgb(self):

        # update the timestamp
        self.run_started = datetime.datetime.utcnow()
        self.save_to_db()

        ds = DataSource.get_by_id(self.data_source_id)
        # train
        xgb = CLF(self)

        if "tf-idf" not in ds.pre_processing_config.values():
            trained_model = xgb.train()
            # populate results
            results_eval, results_model = xgb.populate_results(trained_model)
        else:
            trained_model = xgb.train_nltk(ds.train_vectors_handler)
            # populate results
            results_eval, results_model = xgb.populate_results_nltk(trained_model, ds.vectorizer_handler)

        self.trained_model_handler = DATABASE.getGridFS().put(dill.dumps(trained_model))
        self.results_eval_handler = DATABASE.getGridFS().put(dill.dumps(results_eval))
        self.results_model_handler = DATABASE.getGridFS().put(dill.dumps(results_model))

        # update the timestamp
        self.run_finished = datetime.datetime.utcnow()
        self.save_to_db()

    def get_features_weights(self):
        pickled_model = DATABASE.getGridFS().get(self.trained_model_handler).read()
        classifier = dill.loads(pickled_model)

        feature_weights = classifier.get_booster().get_fscore()
        sorted_fw = OrderedDict(sorted(feature_weights.items(), key=lambda t: t[0]))
        sorted_keys = sorted(self.features.keys())
        print sorted_fw

        feat_importances = []
        for (ft, score) in sorted_fw.items():
            index = int(ft.split("f")[1])
            feat_importances.append({'Feature': sorted_keys[index], 'Importance': score})
        feat_importances = pd.DataFrame(feat_importances)
        feat_importances = feat_importances.sort_values(
            by='Importance', ascending=True).reset_index(drop=True)
        # Divide the importances by the sum of all importances
        # to get relative importances. By using relative importances
        # the sum of all importances will equal to 1, i.e.,
        # np.sum(feat_importances['importance']) == 1
        feat_importances['Importance'] /= feat_importances['Importance'].sum()
        feat_importances = feat_importances.round(3)
        return feat_importances