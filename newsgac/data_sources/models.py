from pymodm import MongoModel, EmbeddedMongoModel, fields
from pymodm.errors import DoesNotExist, ValidationError

from newsgac.common.mixins import CreatedUpdated
from newsgac.genres import genre_codes
from newsgac.data_sources.validators import has_extension
from newsgac.tasks.models import TrackedTask
from newsgac.users.models import User


class Article(MongoModel):
    raw_text = fields.CharField()
    date = fields.DateTimeField()
    year = fields.IntegerField()
    label = fields.IntegerField(max_value=len(genre_codes)-1)


class DataSource(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    filename = fields.CharField(required=True, validators=[has_extension('txt', 'csv')])
    display_title = fields.CharField(required=True)
    description = fields.CharField(required=True)
    file = fields.FileField(required=True)
    training_purpose = fields.BooleanField(required=True, default=False)
    articles = fields.ListField(fields.ReferenceField(Article))

    task = fields.EmbeddedDocumentField(TrackedTask, default=TrackedTask())

    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    def delete(self):
        if self.file:
            self.file.delete()

        from newsgac.ace import ACE
        for ace in ACE.objects.raw({'data_source': self.pk}):
            ace.delete()

        super(DataSource, self).delete()

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
