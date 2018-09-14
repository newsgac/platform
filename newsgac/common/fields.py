from enum import Enum
from pymodm import CharField, FileField
from pymodm.base.fields import MongoBaseField
from pymodm.errors import ValidationError

from newsgac.common.utils import hash_password, is_hashed_password

from dill import dill


class PasswordField(CharField):
    @staticmethod
    def hash(value):
        return hash_password(value)

    def to_mongo(self, value):
        if is_hashed_password(value):
            return value
        return PasswordField.hash(value)


class ObjectField(FileField):
    def to_mongo(self, value):
        return super(self, dill.dumps(value))

    def to_python(self, value):
        return dill.loads(super(self, value))


def enum_validator(enum):
    def validator(value):
        if value not in enum:
            raise ValidationError('value {0} not allowed, valid choices are: {1}'.format(value, enum))
    return validator


class EnumField(MongoBaseField):
    def __init__(self, choices, **kwargs):
        if not issubclass(choices, Enum):
            raise TypeError('EnumField: choices is not a subclass of Enum')
        self.choices_enum = choices
        super(EnumField, self).__init__(**kwargs)
        self.validators.append(enum_validator(choices))

    def to_mongo(self, value):
        # value is an Enum val
        return value.value

    def to_python(self, value):
        return self.choices_enum(value)

