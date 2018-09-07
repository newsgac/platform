from pymodm import CharField

from src.common.utils import hash_password


class PasswordField(CharField):

    def to_mongo(self, value):
        return hash_password(value)
