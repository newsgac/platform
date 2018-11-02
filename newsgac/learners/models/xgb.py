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
            learning_rate=0.1,
            n_estimators=self.parameters.n_estimators,
            silent=True,
            objective="binary:logistic",
            booster='gbtree',
            n_jobs=config.n_parallel_jobs,
            gamma=0,
            min_child_weight=1,
            max_delta_step=0,
            subsample=1,
            colsample_bytree=1,
            colsample_bylevel=1,
            reg_alpha=0,
            reg_lambda=1,
            scale_pos_weight=1,
            base_score=0.5,
            random_state=self.parameters.random_state,
            missing=None,
        )
