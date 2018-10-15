from pymodm import MongoModel, fields

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated


class Cache(CreatedUpdated, MongoModel):
    hash = fields.CharField(required=True)
    data = ObjectField()
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    def delete(self):
        ObjectField.delete(self.hash)
        super(Cache, self).delete()
