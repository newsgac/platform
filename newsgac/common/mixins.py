from datetime import datetime

from pymodm import DateTimeField, EmbeddedDocumentField

from newsgac.common.utils import model_to_dict


class CreatedUpdated(object):
    created = DateTimeField()
    updated = DateTimeField()

    def __init__(self, *args, **kwargs):
        super(CreatedUpdated, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        if not self.created:
            self.created = datetime.now()
        self.updated = datetime.now()
        super(CreatedUpdated, self).save(**kwargs)


class ParametersMixin(object):
    def set_default_parameters(self):
        fields = self.__class__.parameter_fields()
        self.parameters = {
            field.attname: field.default
            for field in fields
        }

    @classmethod
    def parameter_fields(cls):
        return cls.parameters.related_model._mongometa.get_fields()

    @classmethod
    def parameter_dict(cls):
        # create a json serializable dict of the subclass definition
        def map_field(field):
            result_field_dict = {'type': field.__class__.__name__}
            field_dict = field.__dict__
            if isinstance(field, EmbeddedDocumentField):
                field_dict = field.__dict__
                result_field_dict['model'] = map(map_field, field.related_model._mongometa.get_fields())
                result_field_dict['attname'] = field_dict['attname']
                result_field_dict['description'] = field_dict['description']
                result_field_dict['default'] = model_to_dict(field.default)
            else:
                attrs = ['attname', 'default', 'choices', 'verbose_name', 'description']
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
        return model