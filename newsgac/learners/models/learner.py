from pymodm import MongoModel, fields

from newsgac.common.mixins import CreatedUpdated
from newsgac.users.models import User


class Learner(CreatedUpdated, MongoModel):
    class Meta:
        collection_name = 'learner'

    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    _tag = fields.CharField(required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    def set_default_parameters(self):
        fields = self.__class__.parameter_fields()
        self.parameters = {
            field.attname: field.default
            for field in fields
        }

    def save(self, **kwargs):
        self._tag = self.__class__.tag
        super(Learner, self).save(**kwargs)

    @classmethod
    def parameter_fields(cls):
        return cls.parameters.related_model._mongometa.get_fields()

    @classmethod
    def new(cls, **kwargs):
        model = cls(**kwargs)
        model.set_default_parameters()
        model.display_title = ""
        return model
