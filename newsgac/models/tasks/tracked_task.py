import datetime
import uuid

import pymongo
from flask import session

from . import constants
from newsgac.database import DATABASE

__author__ = 'tom'


class Status:
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class TrackedTask(object):
    collection = constants.COLLECTION
    @classmethod
    def create(cls, name, task_args, task_kwargs, *args, **kwargs):
        task = cls()
        task._id = uuid.uuid4().hex
        task.created = datetime.datetime.utcnow()
        task.name = name
        task.task_args = task_args
        task.task_kwargs = task_kwargs
        task.status = Status.PENDING
        task.results = []
        task.user_email = session.get('email', None)
        task.__dict__.update(kwargs)
        return task

    @classmethod
    def get_by_id(cls, id):
        task = TrackedTask()
        task.__dict__.update(**DATABASE.find_one(constants.COLLECTION, {"_id": id}))
        return task

    @classmethod
    def find_one(cls, criteria):
        task = TrackedTask()
        task.__dict__.update(**DATABASE.find_one(constants.COLLECTION, criteria))
        return task

    @classmethod
    def get_all(cls):
        return list(DATABASE.find(constants.COLLECTION, {}))

    @classmethod
    def get_all_by_user_email(cls, user_email):
        return list(DATABASE.find(constants.COLLECTION, {'user_email': user_email}).sort('created', pymongo.DESCENDING))[:5]

    def save_to_db(self):
        DATABASE.update(constants.COLLECTION, {"_id": self._id}, self.__dict__)