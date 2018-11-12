from pymodm import EmbeddedMongoModel
from pymodm import fields
from lightgbm import LGBMClassifier

from newsgac import config
from newsgac.genres import genre_codes
from .learner import Learner


class Parameters(EmbeddedMongoModel):
    n_estimators = fields.IntegerField(required=True, default=100)
    n_estimators.description = 'Number of boosted trees to fit.'

    boosting_type = fields.CharField(
        verbose_name="Boosting type",
        required=True,
        default='gbdt',
        choices=[
            ('gbdt', 'traditional Gradient Boosting Decision Tree'),
            ('dart', 'Dropouts meet Multiple Additive Regression Trees'),
            ('goss', 'Gradient-based One-Side Sampling'),
            ('rf', 'Random Forest'),
        ]
    )
    boosting_type.description = 'Boosting type.'

    max_depth = fields.IntegerField(required=True, default=-1)
    max_depth.description = 'The maximum depth of the tree. -1 is unlimited.'

    num_leaves = fields.IntegerField(required=True, default=31)
    num_leaves.description = 'Maximum tree leaves for base learners.'

    learning_rate = fields.FloatField(required=True, default=0.1)
    learning_rate.description = 'Boosting learning rate.'

    random_state = fields.IntegerField(required=True, default=42)
    random_state.description = 'Enter an integer for a random seed.'

class LearnerLGBM(Learner):
    name = 'Light GBM'
    tag = 'lgbm'
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
        return LGBMClassifier(
            n_estimators=self.parameters.n_estimators,
            random_state=self.parameters.random_state,
            max_depth=self.parameters.max_depth,
            boosting_type=self.parameters.boosting_type,

            num_leaves=self.parameters.num_leaves,
            learning_rate=self.parameters.learning_rate,

            subsample_for_bin=200000,
            objective='multiclass',
            metric='multi_logloss',
            num_class=len(genre_codes),
            class_weight=None,
            min_split_gain=0.0,
            min_child_weight=0.001,

            min_child_samples=20,
            subsample=1.0,
            subsample_freq=0,
            colsample_bytree=1.0,
            reg_alpha=0.0,
            reg_lambda=0.0,

            n_jobs=config.n_parallel_jobs,
            silent=True,
            importance_type='split',
        )
