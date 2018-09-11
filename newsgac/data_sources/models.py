import itertools
import operator

from pymodm import MongoModel, EmbeddedMongoModel, fields, files
from pymodm.errors import DoesNotExist, ValidationError

from newsgac.common.mixins import CreatedUpdated
from newsgac.data_sources.errors import ResourceNotProcessedError, ResourceError
from newsgac.tasks.models import TrackedTask, Status
from newsgac.users.models import User

import newsgac.data_engineering.utils as DataUtils

def is_unique(field_name):
    # todo: is broken (not valid when updating)
    def test_unique(value):
        try:
            DataSource.objects.get({field_name: value})
            raise ValidationError('%s is not unique: ' % value)
        except DoesNotExist:
            pass
    return test_unique


def has_extension(*extensions):
    def test_extension(value):
        if '.' not in value or value.split('.')[-1].lower() not in extensions:
            raise ValidationError('File extension not allowed')
    return test_extension


class Article(EmbeddedMongoModel):
    raw_text = fields.CharField()
    date = fields.DateTimeField()
    year = fields.IntegerField()
    label = fields.CharField()




class DataSource(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    filename = fields.CharField(required=True, validators=[has_extension('txt', 'csv')])
    display_title = fields.CharField(required=True)
    description = fields.CharField(required=True)
    file = fields.FileField(required=True)
    articles = fields.EmbeddedDocumentListField(Article)
    task = fields.ReferenceField(TrackedTask)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    def status(self):
        if self.task:
            return self.task.status
        else:
            return 'UNKNOWN'

    def count_labels(self):
        if not self.status() == Status.SUCCESS:
            raise ResourceNotProcessedError('DataSource has not been processed (yet)')
        get_item = operator.attrgetter('label')
        return {DataUtils.genre_codebook_friendly[k]: len(list(g)) for k, g in
                       itertools.groupby(sorted(self.articles, key=get_item), get_item)}

    def process(self):
        if self.status() in [Status.SUCCESS, Status.STARTED]:
            raise ResourceError('Resource already processed or in progress')
