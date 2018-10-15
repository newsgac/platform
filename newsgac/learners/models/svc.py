from pymodm import EmbeddedMongoModel
from pymodm import fields

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
    random_state.description = 'Enter an integer for ws random seed.'


class LearnerSVC(Learner):
    name = 'Support Vector'
    tag = 'svc'
    parameters = fields.EmbeddedDocumentField(Parameters)
