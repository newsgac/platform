from uuid import UUID

from pymodm import MongoModel, fields

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin
from newsgac.data_sources.models import DataSource
from newsgac.pipelines.models import Pipeline
from newsgac.tasks.models import TrackedTask
from newsgac.users.models import User


# Analyze, compare, explain
class ACE(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    data_source = fields.ReferenceField(DataSource)
    pipelines = fields.ListField(fields.ReferenceField(Pipeline))
    predictions = ObjectField()
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    task_id = fields.CharField()

    @property
    def task(self):
        return TrackedTask.objects.get({"_id": UUID(self.task_id)})
