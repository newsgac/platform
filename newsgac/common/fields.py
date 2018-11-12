import gridfs
from bson import ObjectId
from enum import Enum
import pymodm.fields
from pymodm.base.fields import MongoBaseField
from pymodm.connection import _get_db
from pymodm.errors import ValidationError

from newsgac.common.utils import hash_password, is_hashed_password

from dill import dill


class PasswordField(pymodm.fields.CharField):

    @staticmethod
    def hash(value):
        return hash_password(value)

    def to_mongo(self, value):
        if is_hashed_password(value):
            return value
        return PasswordField.hash(value)


class WrappedObject(object):
    _object = None
    _object_id = None
    _dirty = False

    def __init__(self, obj=None, object_id=None):
        self._object = obj
        if obj is not None and object_id is None:
            self._dirty = True
        self._object_id = object_id

    def get(self):
        if self._object is None and self._object_id is not None:
            fs = gridfs.GridFS(_get_db())
            self._object = dill.loads(fs.get(self._object_id).read())
        return self._object

    def set(self, obj):
        self._object = obj
        self._dirty = True

    def get_object_id(self):
        return self._object_id

    def save(self):
        if self._dirty:
            self.delete(clear_object=False)
            fs = gridfs.GridFS(_get_db())
            self._object_id = fs.put(dill.dumps(self._object))
        self._dirty = False

    def delete(self, clear_object=True):
        if self._object_id:
            db = _get_db()
            fs = gridfs.GridFS(db)
            fs.delete(self._object_id)
            self._object_id = None
            if clear_object:
                self._object = None
                self._dirty = False
            else:
                self._dirty = True

    def is_dirty(self):
        return self._dirty


class ObjectField(pymodm.fields.MongoBaseField):
    def __set__(self, inst, value):
        if inst is not None:
            current_value = getattr(inst, self.attname)
            if current_value is None:
                super(ObjectField, self).__set__(inst, WrappedObject(obj=value))
            else:
                # current_value instanceof WrappedObject
                current_value.set(value)

    def is_blank(self, value):
        return value is None or value.get() is None

    def to_mongo(self, value):
        if value is not None and value.get() is not None:
            value.save()
            return value._object_id
        else:
            return None

    def to_python(self, value):
        if isinstance(value, ObjectId):
            return super(ObjectField, self).to_python(WrappedObject(object_id=value))
        return super(ObjectField, self).to_python(value)

    def validate(self, value):
        return True
    # @staticmethod
    # def delete(hash, db_name='cache'):
    #     data_ref = _get_db()[db_name].find_one({'hash': hash}).get('data', None)
    #     if data_ref:
    #         fs = gridfs.GridFS(_get_db())
    #         fs.delete(data_ref)


def enum_validator(enum):
    def validator(value):
        if value not in enum:
            raise ValidationError('value {0} not allowed, valid choices are: {1}'.format(value, enum))
    return validator


class EnumField(MongoBaseField):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        if not issubclass(choices, Enum):
            raise TypeError('EnumField: choices is not a subclass of Enum')
        self.choices_enum = choices
        super(EnumField, self).__init__(*args, **kwargs)
        self.validators.append(enum_validator(choices))

    def to_mongo(self, value):
        # value is an Enum val
        return value.value

    def to_python(self, value):
        return self.choices_enum(value)
