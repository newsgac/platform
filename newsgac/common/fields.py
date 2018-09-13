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
    def __init__(self, verbose_name=None, mongo_name=None, primary_key=False, blank=False, required=False, default=None,
                 choices=None, validators=None):
        if not issubclass(choices, Enum):
            raise Exception('EnumField: Choices is not a subclass of Enum')
        self.choices_enum = choices
        super(EnumField, self).__init__(verbose_name, mongo_name, primary_key, blank, required, default, None,
                                        validators)
        self.validators.append(enum_validator(choices))

    def to_mongo(self, value):
        # value is an Enum val
        return value.value

    def to_python(self, value):
        return self.choices_enum(value)

