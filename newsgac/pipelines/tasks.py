import subprocess
import sys

from bson import ObjectId

from newsgac.tasks.celery_app import celery_app
from newsgac.tasks.models import Status

from newsgac.pipelines.grid_search import run_grid_search
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.run import run_pipeline


def run_pipeline_task_impl(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    pipeline.task.set_started()
    pipeline.save()
    try:
        run_pipeline(pipeline)
        pipeline.task.set_success()
        pipeline.save()
    except Exception as e:
        t, v, tb = sys.exc_info()
        pipeline.refresh_from_db()
        pipeline.task.set_failure(e)
        pipeline.save()
        raise t(v).with_traceback(tb)

@celery_app.task(bind=True)
def run_pipeline_task(self, pipeline_id):
    # run_pipeline_task_impl(pipeline_id)

    process = subprocess.Popen(['python'], stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate("""
import newsgac.database
from newsgac.pipelines.tasks import run_pipeline_task_impl
run_pipeline_task_impl('%s')
        """ % pipeline_id)

    exit_code = process.wait()

    print(exit_code)
    print(stderrdata)
    print(stdoutdata)


def run_grid_search_task_impl(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    pipeline.task.set_started()
    pipeline.save()
    try:
        run_grid_search(pipeline)
        pipeline.task.set_success()
        pipeline.save()
    except Exception as e:
        t, v, tb = sys.exc_info()
        pipeline.task.status = Status.FAILURE
        pipeline.task.set_failure(e)
        pipeline.save()
        raise t(v).with_traceback(tb)

    # wait for grid search task to be finished
    # TODO: these to be added to celery task after completion of grid search
    # pipeline.learner = create_learner(None, False, **pipeline.grid_search_result['best'])
    # run_pipeline_task.delay(str(pipeline._id))


@celery_app.task(bind=True)
def run_grid_search_task(self, pipeline_id):
    process = subprocess.Popen(['python'], stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate("""
import newsgac.database
from newsgac.pipelines.tasks import run_grid_search_task_impl
run_grid_search_task_impl('%s')
    """ % pipeline_id)

    exit_code = process.wait()

    print(exit_code)
    print(stderrdata)
    print(stdoutdata)
