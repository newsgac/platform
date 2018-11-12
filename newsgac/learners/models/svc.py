from pymodm import EmbeddedMongoModel
from pymodm import fields
from sklearn import svm

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    kernel = fields.CharField(
        verbose_name="Kernel type",
        required=True,
        default='linear',
        choices=[
            ('linear', 'Linear'),
            ('poly', 'Polynomial'),
            ('rbf', 'Radial Basis Function'),
            ('sigmoid', 'Sigmoid'),
        ]
    )
    kernel.description = 'The kernel type to be used in the algorithm.'

    penalty_parameter_c = fields.FloatField(required=True, default=1.0)
    penalty_parameter_c.description = 'Penalty parameter C of the error term.'

    random_state = fields.IntegerField(required=True, default=42)
    random_state.description = 'Enter an integer for a random seed.'


class LearnerSVC(Learner):
    name = 'Support Vector'
    tag = 'svc'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_classifier(self):
        return svm.SVC(
            kernel=self.parameters.kernel,
            C=self.parameters.penalty_parameter_c,
            random_state=self.parameters.random_state,
            decision_function_shape='ovr',
            # class_weight=self.class_weight,
            class_weight='balanced',
            probability=True,
            gamma=0.1
        )

    def get_features_weights(self):
        # check if kernel is linear
        if self.parameters.kernel == 'linear':
            return self.trained_model.steps[-1][1].coef_
