from uuid import UUID

from pymodm import MongoModel, fields

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin
from newsgac.data_sources.models import DataSource
from newsgac.pipelines.models import Pipeline
from newsgac.tasks.models import TrackedTask
from newsgac.users.models import User
import spacy

DUTCH_NLP = spacy.load('nl_core_news_sm')


# Analyze, compare, explain
class ACE(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    data_source = fields.ReferenceField(DataSource)
    pipelines = fields.ListField(fields.ReferenceField(Pipeline))
    predictions = ObjectField()
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    task = fields.EmbeddedDocumentField(TrackedTask, default=TrackedTask())

