from bson import ObjectId

from newsgac.cached_views.models import CachedView
from newsgac.tasks.celery_app import celery_app


@celery_app.task()
def save_view_task_result(result, cache_id):
    cache = CachedView.objects.get({'_id': ObjectId(cache_id)})
    cache.task.set_success()
    cache.data = result
    cache.save()


@celery_app.task()
def save_view_task_result_error(task, error, _, cache_id):
    cache = CachedView.objects.get({'_id': ObjectId(cache_id)})
    cache.task.set_failure(error)
    cache.save()
