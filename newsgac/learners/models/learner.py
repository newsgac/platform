from pymodm import MongoModel, fields, EmbeddedMongoModel

from newsgac.common.mixins import CreatedUpdated
from newsgac.users.models import User


class Learner(CreatedUpdated, EmbeddedMongoModel):
    class Meta:
        collection_name = 'learner'

    _tag = fields.CharField(required=True)

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
    def parameter_dict(cls):
        def map_field(field):
            attrs = ['attname', 'default', 'choices', 'verbose_name', 'description']
            field_dict = field.__dict__
            result_field_dict = {'type': field.__class__.__name__}
            for attr in attrs:
                if attr in field_dict.keys():
                    result_field_dict[attr] = field_dict[attr]
            return result_field_dict

        result = map(map_field, cls.parameters.related_model._mongometa.get_fields())
        return result

    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        model.set_default_parameters()
        model._tag = cls.tag
        return model
