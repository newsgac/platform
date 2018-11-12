from datetime import datetime

from pymodm import MongoModel, fields
from pymodm.errors import DoesNotExist, MultipleObjectsReturned
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
            cache = cls.objects.raw({'hash': hash})[0]
            cache.last_accessed = datetime.utcnow()
            cache.save()
            return cache
        except DoesNotExist:
            return cls(hash=hash)


    def delete(self):
        self.data.delete()
        super(Cache, self).delete()
