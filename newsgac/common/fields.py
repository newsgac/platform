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


class ObjectField(pymodm.fields.MongoBaseField):

    def is_blank(self, value):
        return value is None

    # def validate(self, value):
    #      and not self.blank:
    #         raise ValidationError('must not be blank (was: %r)' % value)

    def to_mongo(self, value):
        fs = gridfs.GridFS(_get_db())
        return fs.put(dill.dumps(value))

    def to_python(self, value):
        if isinstance(value, ObjectId):
            fs = gridfs.GridFS(_get_db())
            return super(ObjectField, self).to_python(dill.loads(fs.get(value).read()))
        return super(ObjectField, self).to_python(value)

    @staticmethod
    def delete(hash):
        data_ref = _get_db()['cache'].find_one({'hash': hash})['data']
        fs = gridfs.GridFS(_get_db())
        fs.delete(data_ref)


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
