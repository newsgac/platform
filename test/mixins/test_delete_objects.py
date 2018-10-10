from pymodm import MongoModel, fields, EmbeddedMongoModel
from pymodm.connection import _get_db

from common.fields import ObjectField
from common.mixins import CreatedUpdated, DeleteObjectsMixin


class EmbeddedModelWithObjectField(EmbeddedMongoModel):
    data = ObjectField()


class ModelWithObjectField(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    data = ObjectField()
    embed = fields.EmbeddedDocumentField(EmbeddedModelWithObjectField)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()


def test_delete_objects():
    m = ModelWithObjectField()
    m.data = "some object"
    m.embed = EmbeddedModelWithObjectField(data="some embedded object")
    m.save()
    db = _get_db()
    assert db['fs.files'].count() == 2
    assert db['fs.chunks'].count() == 2
    assert ModelWithObjectField.objects.count() == 1
    m.delete()
    assert db['fs.files'].count() == 0
    assert db['fs.chunks'].count() == 0
    assert ModelWithObjectField.objects.count() == 0
