from pymodm import EmbeddedMongoModel, fields

from newsgac.common.mixins import ParametersMixin


class NlpTool(ParametersMixin, EmbeddedMongoModel):
    _tag = fields.CharField(required=True)
