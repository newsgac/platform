from pymodm import MongoModel, fields
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin
from newsgac.users.models import User


# Analyze, compare, explain
class ACE(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    task_id = fields.CharField()

