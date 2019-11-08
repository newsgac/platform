from pymodm import MongoModel, fields

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin

from newsgac.tasks.models import TrackedTask


# Analyze, compare, explain
class ACE(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    from newsgac.pipelines.models import Pipeline
    from newsgac.data_sources.models import DataSource
    from newsgac.users.models import User

    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    data_source = fields.ReferenceField(DataSource)
    pipelines = fields.ListField(fields.ReferenceField(Pipeline))
    predictions = ObjectField(blank=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    task = fields.EmbeddedDocumentField(TrackedTask, default=TrackedTask())

    def get_display_title(self):
        return self.data_source.display_title + ' (' + ', '.join(
            p.display_title for p in self.pipelines) + ')'

    def delete_pipeline(self, pipeline):
        self.pipelines.remove(pipeline)
        if len(self.pipelines) == 0:
            self.delete()
        else:
            # rerun...
            # self.predictions.delete()
            self.predictions = ObjectField(blank=True)
            self.display_title = self.get_display_title()
            self.task = TrackedTask()
            self.save()
            from newsgac.ace.tasks import run_ace
            run_ace.delay(self.pk)
