from datetime import datetime

import gridfs
from pymodm import DateTimeField, EmbeddedDocumentField
from pymodm.connection import _get_db

from common.fields import ObjectField
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


class DeleteObjectsMixin(object):
    # Use this mixin on model classes that have ObjectFields,
    # So they get cleaned up when the model is deleted.
    # it recursively deletes ObjectFields on EmbeddedDocuments also
    def delete(self):
        db = _get_db()
        fs = gridfs.GridFS(db)

        object_field_paths = []
        def delete_objects_in_field(field, path):
            if isinstance(field, ObjectField):
                object_field_paths.append(path + [field.attname])
            if isinstance(field, EmbeddedDocumentField):
                for sub_field in field.related_model._mongometa.get_fields():
                    delete_objects_in_field(sub_field, path + [field.attname])
        for field in self._mongometa.get_fields():
            delete_objects_in_field(field, [])

        # delete grid fs files from object_paths
        raw_document = db[self._mongometa.collection_name].find_one({'_id': self.pk})
        for path in object_field_paths:
            current = raw_document
            for path_part in path:
                current = current[path_part]
            fs.delete(current)
        super(DeleteObjectsMixin, self).delete()


class ParametersMixin(object):
    # Parameters represent user configurable settings (of nlp_tools or machine learners)
    # class should have a `parameters` field that is an EmbeddedDocument
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
        # create a json serializable dict of the parameters definition of this class
        def map_field(field):
            result_field_dict = {'type': field.__class__.__name__}
            field_dict = field.__dict__
            if isinstance(field, EmbeddedDocumentField):
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