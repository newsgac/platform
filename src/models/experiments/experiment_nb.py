import datetime

from src.database import DATABASE
from src.machine_learning.clf import CLF
from src.models.configurations.configuration_nb import ConfigurationNB
from src.models.data_sources.data_source_old import DataSource
from src.models.experiments import constants as ExperimentConstants
from src.models.experiments.experiment import Experiment


class ExperimentNB(Experiment, ConfigurationNB):
    type = 'NB'
    def __init__(self, user_email, display_title, public_flag, **kwargs):
        ConfigurationNB.__init__(self, user_email, **kwargs)
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
        ConfigurationNB.delete(self)
        DATABASE.remove(ExperimentConstants.COLLECTION, {'_id': id})

    def run(self):
        self.run_nb()

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

        self.trained_model_handler = DATABASE.save_object(trained_model)
        self.results_eval_handler = DATABASE.save_object(results_eval)
        self.results_model_handler = DATABASE.save_object(results_model)

        # update the timestamp
        self.run_finished = datetime.datetime.utcnow()
        self.save_to_db()

    def get_features_weights(self):
        classifier = DATABASE.load_object(self.trained_model_handler)
        return classifier.coef_