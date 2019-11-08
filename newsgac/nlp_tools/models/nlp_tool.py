from pymodm import EmbeddedMongoModel

from newsgac.common.mixins import ParametersMixin


class NlpTool(ParametersMixin, EmbeddedMongoModel):
    pass
