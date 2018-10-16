from datetime import datetime

from pymodm import MongoModel, fields
from pymodm.errors import DoesNotExist
from pymongo import IndexModel

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin


class Cache(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    hash = fields.CharField(required=True)
    data = ObjectField()
    created = fields.DateTimeField()
    updated = fields.DateTimeField()
    last_accessed = fields.DateTimeField()

    class Meta:
        indexes = [IndexModel([('hash', 1)])]

    @classmethod
    def get_or_new(cls, hash):
        try:
            cache = cls.objects.get({'hash': hash})
            cache.last_accessed = datetime.utcnow()
            cache.save()
            return cache
        except DoesNotExist:
            return cls(hash=hash)

    def delete(self):
        ObjectField.delete(self.hash)
        super(Cache, self).delete()
