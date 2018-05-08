import uuid

from run import DATABASE
from src.common.utils import Utils
import src.models.users.errors as UserErrors
import src.models.users.constants as UserConstants


UT = Utils()

__author__ = 'abilgin'

class User(object):

    def __init__(self, username, name, surname, email, password, _id=None):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {} {} - {}>".format(self.name, self.surname, self.email)

    @staticmethod
    def is_login_valid(identifier, password):
        user_data_by_email = DATABASE.find_one(UserConstants.COLLECTION, {"email": identifier})
        user_data_by_username = DATABASE.find_one(UserConstants.COLLECTION, {"username": identifier})

        if (user_data_by_email is None) and (user_data_by_username is None):
            raise UserErrors.UserNotExistsError("The username/email does not exist.")

        if user_data_by_username is not None:
            user = user_data_by_username
        else:
            user = user_data_by_email

        if not UT.check_hashed_password(password, user['password']):
            raise UserErrors.IncorrectPasswordError("The password is incorrect.")

        return True

    @staticmethod
    def register_user(username, name, surname, email, password):
        user_data_by_email = DATABASE.find_one(UserConstants.COLLECTION, {"email": email})
        user_data_by_username = DATABASE.find_one(UserConstants.COLLECTION, {"username": username})

        if user_data_by_email is not None:
            raise UserErrors.UserAlreadyRegisteredError("The e-mail address already exists.")

        if user_data_by_username is not None:
            raise UserErrors.UsernameTakenError("The username is already taken.")

        if not UT.email_is_valid(email):
            raise UserErrors.InvalidEmailError("The e-mail address does not have the right format.")

        User(username, name, surname, email, UT.hash_password(password)).save_to_db()

        return True

    def save_to_db(self):
        DATABASE.insert(UserConstants.COLLECTION, self.json())

    def json(self):
        return {
            "_id": self._id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "password": self.password
        }

    @classmethod
    def get_by_email(cls, email):
        return cls(**DATABASE.find_one(UserConstants.COLLECTION, {"email": email}))

    @classmethod
    def get_by_identifier(cls, identifier):
        user_data = DATABASE.find_one(UserConstants.COLLECTION, {"email": identifier})
        if user_data is None:
            return cls(**DATABASE.find_one(UserConstants.COLLECTION, {"username": identifier}))
        return cls(**user_data)
