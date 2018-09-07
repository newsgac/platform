from pymodm import MongoModel, EmbeddedMongoModel, fields, files
from pymodm.errors import DoesNotExist, ValidationError

from newsgac.common.mixins import CreatedUpdated
from newsgac.users.models import User


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
    user = fields.ReferenceField(User)
    filename = fields.CharField(validators=[has_extension('txt', 'csv')])
    display_title = fields.CharField()
    description = fields.CharField()
    file = fields.FileField()
    articles = fields.EmbeddedDocumentListField(Article)
    task_id = fields.CharField()
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

