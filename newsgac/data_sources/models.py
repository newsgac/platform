import itertools
import operator

from pymodm import MongoModel, EmbeddedMongoModel, fields
from pymodm.errors import DoesNotExist, ValidationError

from newsgac.common.mixins import CreatedUpdated
from newsgac.data_sources.errors import ResourceNotProcessedError, ResourceError
from newsgac.data_sources.validators import has_extension
from newsgac.tasks.models import TrackedTask, Status
from newsgac.users.models import User

import newsgac.data_engineering.utils as DataUtils


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

    def full_clean(self, exclude=None):
        super(DataSource, self).full_clean(exclude)
        if not self._id:
            try:
                DataSource.objects.get({'display_title': self.display_title})
            except DoesNotExist as e:
                return
            raise ValidationError('Display title exists')



    def count_labels(self):
        if not self.status() == Status.SUCCESS:
            raise ResourceNotProcessedError('DataSource has not been processed (yet)')
        get_item = operator.attrgetter('label')
        return {
            DataUtils.genre_codebook_friendly[k]: len(list(g)) for k, g in
            itertools.groupby(sorted(self.articles, key=get_item), get_item)
        }

    def process(self):
        if self.status() in [Status.SUCCESS, Status.STARTED]:
            raise ResourceError('Resource already processed or in progress')
