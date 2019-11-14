from pymodm import EmbeddedMongoModel
from newsgac.common.mixins import ParametersMixin


class Learner(ParametersMixin, EmbeddedMongoModel):
    pass
