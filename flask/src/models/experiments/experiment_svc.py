import datetime

import dill

from src.database import DATABASE
from src.machine_learning.clf import CLF
from src.models.configurations.configuration_svc import ConfigurationSVC
from src.models.data_sources.data_source import DataSource
from src.models.experiments import constants as ExperimentConstants
from src.models.experiments.experiment import Experiment


class ExperimentSVC(Experiment, ConfigurationSVC):
    type = 'SVC'
    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationSVC.__init__(self, user_email, **kwargs)
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
        ConfigurationSVC.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})
        DATABASE.updateManyForRemoval('predictions', "exp_predictions." + id)

    def run(self):
        self.run_svc()

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