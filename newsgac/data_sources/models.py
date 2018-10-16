from pymodm import MongoModel, EmbeddedMongoModel, fields
from pymodm.errors import DoesNotExist, ValidationError

from newsgac.common.mixins import CreatedUpdated
from newsgac.data_sources.validators import has_extension
from newsgac.tasks.models import TrackedTask
from newsgac.users.models import User


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
        if not self._id:  # ensure unique display_title
            try:
                DataSource.objects.get({'display_title': self.display_title})
            except DoesNotExist as e:
                return
            raise ValidationError('Display title exists')
