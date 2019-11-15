from datetime import datetime

from traceback import format_exception, format_exc

from enum import Enum
from pymodm import fields, EmbeddedMongoModel, DateTimeField

from newsgac.common.fields import EnumField


class Status(Enum):
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class TrackedTask(EmbeddedMongoModel):
    status = EnumField(required=True, choices=Status, default=Status.QUEUED)
    error = fields.CharField(blank=True)
    start = DateTimeField(blank=True)
    end = DateTimeField(blank=True)
    trace = fields.CharField(blank=True)
    task_id = fields.CharField()

    def set_started(self):
        self.status = Status.STARTED
        self.start = datetime.now()

    def set_success(self):
        self.status = Status.SUCCESS
        self.end = datetime.now()

    def set_failure(self, err):
        self.status = Status.FAILURE
        self.end = datetime.now()
        self.error = str(err)
        import sys
        # self.trace = sys.exc_info()
        self.trace = format_exc()
