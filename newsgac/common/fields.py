from pymodm import CharField, FileField

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
