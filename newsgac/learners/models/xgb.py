from pymodm import EmbeddedMongoModel
from pymodm import fields
from xgboost import XGBClassifier

from newsgac import config
from .learner import Learner


class Parameters(EmbeddedMongoModel):
    n_estimators = fields.IntegerField(required=True, default=100)
    n_estimators.description = 'Number of boosted trees to fit.'

    learning_rate = fields.FloatField(
        verbose_name="Learning rate",
        required=True,
        default=0.1
    )
    learning_rate.description = 'Boosting learning rate (xgb\'s "eta")'

    booster = fields.CharField(
        verbose_name="Booster",
        required=True,
        default='gbtree',
        choices=[
            ('gbtree', 'gbtree'),
            ('gblinear', 'gblinear'),
            ('dart', 'dart'),
        ]
    )
    booster.description = 'Specify which booster to use.'

    max_depth = fields.IntegerField(required=True, default=3)
    max_depth.description = 'Maximum tree depth for base learners.'

    random_state = fields.IntegerField(required=True, default=42)
    random_state.description = 'Enter an integer for a random seed.'

    gamma = fields.FloatField(required=False, default=0)
    gamma.description = 'Minimum loss reduction required to make a further partition on a leaf node of the tree.'

    min_child_weight = fields.IntegerField(required=False, default=1)
    min_child_weight.description = 'Minimum sum of instance weight needed in a child.'

    colsample_bytree = fields.FloatField(required=False, default=1)
    colsample_bytree.description = 'Subsample ratio of columns when constructing each tree.'

    subsample = fields.FloatField(required=False, default=1)
    subsample.description = 'Subsample ratio of the training instance.'

    importance_type = fields.CharField(
        verbose_name="Importance type",
        required=False,
        default='gain',
        choices=[
            ('gain', 'Gain'),
            ('weight', 'Weight'),
            ('cover', 'Cover'),
            ('total_gain', 'Total gain'),
            ('total_cover', 'Total cover'),
        ]
    )
    importance_type.description = 'The feature importance type for the feature_importances_ property. Only defined for gbtree booster.'

class LearnerXGB(Learner):
    name = 'XGBoost'
    tag = 'xgb'
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
        return XGBClassifier(
            max_depth=self.transform_0_to_none(self.parameters.max_depth),
            learning_rate=self.parameters.learning_rate,
            n_estimators=self.parameters.n_estimators,
            booster=self.parameters.booster,
            gamma=self.parameters.gamma,
            min_child_weight=self.parameters.min_child_weight,
            colsample_bytree=self.parameters.colsample_bytree,
            subsample=self.parameters.subsample,
            importance_type=self.parameters.importance_type,
            random_state=self.parameters.random_state,

            silent=True,
            objective="multi:softprob",
            n_jobs=config.n_parallel_jobs,
            max_delta_step=0,
            colsample_bylevel=1,
            reg_alpha=0,
            reg_lambda=1,
            scale_pos_weight=1,
            base_score=0.5,
            missing=None,
        )
