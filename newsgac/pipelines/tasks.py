from bson import ObjectId
from celery import current_task

from newsgac.pipelines.grid_search import run_grid_search
from newsgac.tasks.celery_app import celery_app
from .models import Pipeline
from .run import run_pipeline
import subprocess


@celery_app.task(bind=True, trail=True)
def run_pipeline_task(self, pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    run_pipeline(pipeline)


def run_grid_search_task_impl(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    run_grid_search(pipeline)

@celery_app.task(bind=True, trail=True)
def run_grid_search_task(self, pipeline_id):

    # from multiprocessing import current_process
    # current_process().daemon = False
    # current_process()._authkey = 'randomKey'
    # current_process()._daemonic = False
    # current_process()._tempdir = '/tmp'
    # pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    # run_grid_search(pipeline)
    process = subprocess.Popen(['python'], stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate("""
import newsgac.database
from newsgac.pipelines.tasks import run_grid_search_task_impl
from newsgac.tasks import progress
progress.task_id = '%s'
run_grid_search_task_impl('%s')
""" % (current_task.request.id, pipeline_id))

    exit_code = process.wait()

    print(exit_code)
    print(stderrdata)
    print(stdoutdata)

    # current_process().daemon = True

#
# @celery_app.task(bind=True, trail=True)
# def run_grid_search_task(self, pipeline_id):
#     pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
#     run_grid_search(pipeline)
