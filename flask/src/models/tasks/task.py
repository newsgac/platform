from . import constants
from src.database import DATABASE

__author__ = 'tom'

class Task(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(constants.COLLECTION, {"_id": id}))

    @classmethod
    def get_all(cls):
        return list(DATABASE.find(constants.COLLECTION, {}))

    @classmethod
    def get_all_by_user_email(cls, user_email):
        return list(DATABASE.find(constants.COLLECTION, {'user_email': user_email}))