from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn.ensemble import GradientBoostingClassifier

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    learning_rate = fields.FloatField(
        verbose_name="Learning rate",
        required=True,
        default=0.1
    )
    learning_rate.description = 'Learning rate shrinks the contribution of each tree by its value.'

    n_estimators = fields.IntegerField(required=True, default=100)
    n_estimators.description = 'Number of boosting stages to perform.'

    max_features = fields.CharField(
        verbose_name="Max features",
        required=True,
        default='auto',
        choices=[
            ('auto', 'Auto'),
            ('sqrt', 'Sqrt'),
            ('log2', 'Log2'),
            # ('none', 'same as nFeatures'),
            ('.5', '50 percent'),
            # ('20', 'max 20 features'),
        ]
    )
    max_features.description = 'The number of features to consider when looking for the best split.'

    loss = fields.CharField(
        verbose_name="Loss",
        required=True,
        default='deviance',
        choices=[
            ('deviance', 'Deviance (logistic regression)'),
            ('exponential', 'Exponential (AdaBoost)'),
        ]
    )
    loss.description = 'The function to measure the quality of a split.'

    # criterion = fields.CharField(
    #     verbose_name="Criterion",
    #     required=True,
    #     default='friedman_mse',
    #     choices=[
    #         ('friedman_mse', 'Friedman mean squared error'),
    #         ('mse', 'Mean squared error'),
    #         ('mae', 'Mean absolute error'),
    #     ]
    # )
    # criterion.description = 'The function to measure the quality of a split.'

    max_depth = fields.IntegerField(required=True, default=3)
    max_depth.description = 'The maximum depth of the tree. If 0, then nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.'

    random_state = fields.IntegerField(required=True, default=42)
    random_state.description = 'Enter an integer for a random seed.'

class LearnerGB(Learner):
    name = 'Gradient Boost (sklearn)'
    tag = 'gb'
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
        return GradientBoostingClassifier(
            learning_rate=self.parameters.learning_rate,
            n_estimators=self.parameters.n_estimators,
            loss=self.parameters.loss,
            max_features=self.transform_max_features(self.parameters.max_features),
            random_state=self.parameters.random_state,
            max_depth=self.transform_0_to_none(self.parameters.max_depth),
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.,
            max_leaf_nodes=None,
            min_impurity_decrease=0.,
            warm_start=False,
            init=None,
            presort='auto',
            validation_fraction=0.1,
            n_iter_no_change=None,
            tol=1e-4,
            verbose=0,
        )
