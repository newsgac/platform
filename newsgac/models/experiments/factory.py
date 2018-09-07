from newsgac.database import DATABASE
from newsgac.models.experiments.experiment_nb import ExperimentNB
from newsgac.models.experiments.experiment_mlp import ExperimentMLP
from newsgac.models.experiments.experiment_rf import ExperimentRF
from newsgac.models.experiments.experiment_xgb import ExperimentXGB
from newsgac.models.experiments.experiment_svc import ExperimentSVC

from . import constants

experiment_classes = [ExperimentNB, ExperimentMLP, ExperimentRF, ExperimentSVC, ExperimentXGB]


def get_experiment_by_id(id):
    db_item = DATABASE.find_one(constants.COLLECTION, {"_id": id})
    if not db_item:
        raise LookupError("No experiment with id %s" % id)
    for exp_class in experiment_classes:
        if exp_class.type == db_item['type']:
            return exp_class(**db_item)
    raise TypeError("No such experiment class type: %s" % db_item['type'])
