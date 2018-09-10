from pymodm import MongoModel, fields, validators
from pymodm.errors import DoesNotExist

from newsgac.common.mixins import CreatedUpdated


class Status:
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    REVOKED = 'REVOKED'


class TrackedTask(CreatedUpdated, MongoModel):
    class Meta:
        collection_name = 'task'

    _id = fields.UUIDField(primary_key=True)
    name = fields.CharField(required=True)
    backend = fields.CharField(required=True, default='celery')
    status = fields.CharField(required=True, default=Status.QUEUED)  # enum validator?
    task_args = fields.ListField(default=[], blank=True)
    task_kwargs = fields.DictField(default={}, blank=True)
    children = fields.ListField(fields.ReferenceField('TrackedTask'), default=[], blank=True)
    parent = fields.ReferenceField('newsgac.tasks.models.TrackedTask', required=False, blank=True)
    result = fields.DictField(default={}, blank=True)
    traceback = fields.CharField(blank=True)

    date_started = fields.DateTimeField()
    date_done = fields.DateTimeField(blank=True)

    created = fields.DateTimeField()
    updated = fields.DateTimeField()

