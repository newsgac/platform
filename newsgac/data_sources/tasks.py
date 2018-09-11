from newsgac.tasks.celery_app import celery_app
from .models import DataSource
from .process import process_data_source

@celery_app.task(bind=True, trail=True)
def process(self, data_source_id):
    data_source = DataSource.objects.get({'_id': data_source_id})
    process_data_source(data_source)
