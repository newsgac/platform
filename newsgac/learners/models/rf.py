from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn.ensemble import RandomForestClassifier

from newsgac import config
from .learner import Learner


class Parameters(EmbeddedMongoModel):
    n_estimators = fields.IntegerField(required=True, default=100)
    n_estimators.description = 'Number of trees in the forest.'

    # max_features = fields.CharField(
    #     verbose_name="Max features",
    #     required=True,
    #     default='auto',
    #     choices=[
    #         ('auto', 'Auto'),
    #         ('sqrt', 'Sqrt'),
    #         ('log2', 'Log2'),
    #         ('none', 'same as nFeatures'),
    #         ('.5', '50 percent'),
    #         ('20', 'max 20 features'),
    #     ]
    # )

    max_features = fields.IntegerField(required=True, default=5)
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

    min_samples_leaf = fields.IntegerField(required=False, default=1)
    min_samples_leaf.description = 'The minimum number of samples required to be at a leaf node.'

    min_samples_split = fields.IntegerField(required=False, default=2)
    min_samples_split.description = 'The minimum number of samples required to split an internal node.'

    max_leaf_nodes = fields.IntegerField(required=False, default=0)
    max_leaf_nodes.description = 'Grow trees with max_leaf_nodes in best-first fashion.'

    bootstrap = fields.BooleanField(required=False, default=True)
    bootstrap.description = 'Whether bootstrap samples are used when building trees.'

    class_weight = fields.CharField(
        verbose_name="Class weight",
        required=False,
        default=None,
        choices=[
            ('none', 'None'),
            ('balanced', 'Balanced'),
        ]
    )
    class_weight.description = 'Weights associated with classes.'


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
            max_features=self.parameters.max_features,
            # max_features=self.transform_max_features(self.parameters.max_features),
            random_state=self.parameters.random_state,
            max_depth=self.transform_0_to_none(self.parameters.max_depth),
            max_leaf_nodes=self.transform_0_to_none(self.parameters.max_leaf_nodes),
            min_samples_split=self.parameters.min_samples_split,
            min_samples_leaf=self.parameters.min_samples_leaf,
            bootstrap=self.parameters.bootstrap,
            class_weight=self.transform_max_features(self.parameters.class_weight),

            min_weight_fraction_leaf=0.,
            min_impurity_decrease=0.,
            oob_score=False,
            verbose=0,
            warm_start=False,
            n_jobs=config.n_parallel_jobs,
        )
