from bson import ObjectId

from newsgac.tasks.celery_app import celery_app
from .models import DataSource
from .process import upload_data_source

@celery_app.task(bind=True, trail=True)
def process(self, data_source_id):
    data_source = DataSource.objects.get({'_id': ObjectId(data_source_id)})
    upload_data_source(data_source)
