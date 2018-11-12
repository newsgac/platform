from bson import ObjectId

from newsgac.tasks.celery_app import celery_app
from newsgac.data_sources.models import DataSource
from newsgac.data_sources.process import get_articles_from_file


@celery_app.task(bind=True, trail=True)
def process(self, data_source_id):
    data_source = DataSource.objects.get({'_id': ObjectId(data_source_id)})
    data_source.articles = get_articles_from_file(data_source.file.file)
    data_source.save()
