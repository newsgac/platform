from pymodm import MongoModel, fields

from newsgac.common.mixins import CreatedUpdated
from newsgac.users.models import User


class StopWords(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    filename = fields.CharField(required=True)
    display_title = fields.CharField(required=True)
    description = fields.CharField(required=True)
    file = fields.FileField(required=True)

    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    def delete(self):
        if self.file:
            self.file.delete()

        super(StopWords, self).delete()

    # def __repr__(self):
    #     return '[DataSource id: {0}]'.format(self._id)

