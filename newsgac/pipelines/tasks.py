from bson import ObjectId

from newsgac.tasks.celery_app import celery_app
from .models import Pipeline
from .run import run_pipeline

@celery_app.task(bind=True, trail=True)
def run_pipeline_task(self, pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    run_pipeline(pipeline)
