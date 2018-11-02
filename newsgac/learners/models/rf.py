from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn.ensemble import RandomForestClassifier

from newsgac import config
from .learner import Learner


class Parameters(EmbeddedMongoModel):
    n_estimators = fields.IntegerField(required=True, default=100)
    n_estimators.description = 'Number of trees in the forest.'

    max_features = fields.CharField(
        verbose_name="Max features",
        required=True,
        default='auto',
        choices=[
            ('auto', 'Auto'),
            ('sqrt', 'Sqrt'),
            ('log2', 'Log2'),
            ('none', 'same as nFeatures'),
            ('.5', '50 percent'),
            ('20', 'max 20 features'),
        ]
    )

    max_features.description = 'The number of features to consider when looking for the best split.'

    random_state = fields.IntegerField(required=True, default=42)
    random_state.description = 'Enter an integer for a random seed.'

    criterion = fields.CharField(
        verbose_name="Criterion",
        required=True,
        default='gini',
        choices=[
            ('gini', 'Gini'),
            ('entropy', 'Entropy'),
        ]
    )
    criterion.description = 'The function to measure the quality of a split.'

    max_depth = fields.IntegerField(required=True, default=0)
    max_depth.description = 'The maximum depth of the tree. If 0, then nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.'


class LearnerRF(Learner):
    name = 'Random Forest'
    tag = 'rf'
    parameters = fields.EmbeddedDocumentField(Parameters)

    @staticmethod
    def transform_max_features(max_features):
        if max_features == 'none':
            return None
        try:
            return int(max_features)
        except ValueError:
            pass
        try:
            return float(max_features)
        except ValueError:
            pass
        return max_features

    @staticmethod
    def transform_0_to_none(par):
        return None if par == 0 else par

    def get_classifier(self):
        return RandomForestClassifier(
            n_estimators=self.parameters.n_estimators,
            max_features=self.transform_max_features(self.parameters.max_features),
            random_state=self.parameters.random_state,
            max_depth=self.transform_0_to_none(self.parameters.max_depth),
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.,
            max_leaf_nodes=None,
            min_impurity_decrease=0.,
            min_impurity_split=None,
            bootstrap=True,
            oob_score=False,
            verbose=0,
            warm_start=False,
            n_jobs=config.n_parallel_jobs,
            class_weight=None
        )
