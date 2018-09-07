from datetime import datetime

from pymodm import DateTimeField


class CreatedUpdated(object):
    created = DateTimeField()
    updated = DateTimeField()

    def __init__(self, *args, **kwargs):
        super(CreatedUpdated, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        if not self.created:
            self.created = datetime.now()
        self.updated = datetime.now()
        super(CreatedUpdated, self).save(**kwargs)
