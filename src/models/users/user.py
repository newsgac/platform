from pymodm import MongoModel, fields

from .password_field import PasswordField


class User(MongoModel):
    email = fields.EmailField(primary_key=True)
    password = PasswordField(min_length=8)

