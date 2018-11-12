from pymodm import MongoModel, fields
from pymodm.errors import DoesNotExist

from newsgac.common.mixins import CreatedUpdated
from newsgac.common.utils import check_hashed_password
from .errors import IncorrectPasswordError, UserNotExistsError
from newsgac.common.fields import PasswordField


class User(CreatedUpdated, MongoModel):
    email = fields.EmailField(primary_key=True)
    password = PasswordField(min_length=8, required=True)
    name = fields.CharField(min_length=1, max_length=50, required=True)
    surname = fields.CharField(min_length=1, max_length=50, required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    @staticmethod
    def from_login(email, password):
        try:
            user = User.objects.get({'_id': email})
        except DoesNotExist:
            raise UserNotExistsError('User does not exist')
        if check_hashed_password(password, user.password):
            return user
        raise IncorrectPasswordError('Incorrect username/password')
