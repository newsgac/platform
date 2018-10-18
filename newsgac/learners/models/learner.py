from pymodm import fields, EmbeddedMongoModel
from newsgac.common.mixins import ParametersMixin


class Learner(ParametersMixin, EmbeddedMongoModel):
    _tag = fields.CharField(required=True)

    def save(self, **kwargs):
        self._tag = self.__class__.tag
        super(Learner, self).save(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        model.set_default_parameters()
        model._tag = cls.tag
        return model


