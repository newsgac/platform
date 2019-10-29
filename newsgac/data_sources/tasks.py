import sys

from bson import ObjectId

from newsgac.data_sources.parsers import get_parser
from newsgac.tasks.celery_app import celery_app
from newsgac.data_sources.models import DataSource


@celery_app.task(bind=True, trail=True)
def process_data_source(self, data_source_id):
    data_source = DataSource.objects.get({'_id': ObjectId(data_source_id)})

    data_source.task.set_started()
    data_source.save()
    try:
        parser = get_parser(data_source.file_format)
        data_source.articles = parser.get_articles_from_data_source(data_source)
        for article in data_source.articles:
            article.save()
        data_source.save()
        data_source.task.set_success()
        data_source.save()
    except Exception as e:
        t, v, tb = sys.exc_info()
        data_source.refresh_from_db()
        data_source.task.set_failure(e)
        data_source.save()
        raise t(v).with_traceback(tb)
