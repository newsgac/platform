import uuid

import redis
from flask import session
from celery import Celery, Task
from kombu.serialization import register

from common.utils import model_to_json
from newsgac import config
from newsgac.tasks.models import TrackedTask, Status
from newsgac.common.json_encoder import _dumps, _loads


register('myjson', _dumps, _loads, content_type='application/x-myjson', content_encoding='utf-8')


class CeleryTrackedTask(Task):
    def apply_async(self, args=None, kwargs=None, **options):
        task_id = options.pop('task_id', str(uuid.uuid4()))
        task = TrackedTask(
            _id=task_id,
            name=self.name,
            status=Status.QUEUED,
            task_args=args or [],
            task_kwargs=kwargs or {},
            backend='celery',
            result={}
        )
        try:
            task.save()
        except Exception as e:
            raise
        client = redis.Redis()
        client.publish("celery_task_new", model_to_json(task))
        task_eager_result = super(CeleryTrackedTask, self).apply_async(args, kwargs, task_id=task_id, headers={'user_email': session['email']}, **options)

        # task.refresh_from_db()
        # task.children = task_eager_result.children or []
        # task.parent = task_eager_result.parent
        # task.save()
        task_eager_result.task = task
        return task_eager_result


celery_app = Celery(
    'newsgac.tasks',
    broker=config.redis_url,
    # backend='rpc://',
    include=[
        'newsgac.tasks',
        'newsgac.data_sources.tasks',
        'newsgac.pipelines.tasks',
        'newsgac.tasks.tasks',
    ],
    task_cls=CeleryTrackedTask
)

celery_app.conf.broker_connection_timeout = 1
celery_app.conf.task_always_eager = config.celery_eager
celery_app.conf.task_ignore_result = False
celery_app.conf.task_track_started = True
# celery_app.conf.result_backend = config.redis_url
celery_app.conf.result_backend = 'newsgac.tasks.celery_mongo_result_backend.ExtendedMongoBackend'
celery_app.conf.accept_content = ['myjson']
celery_app.conf.task_serializer = 'myjson'
celery_app.conf.result_serializer = 'myjson'
# celery_app.conf.mongodb_backend_settings = {
#     'host': config.mongo_host,
#     'port': config.mongo_port,
#     'database': config.mongo_database_name,
    # 'taskmeta_collection': 'celery_tasks',
# }
from newsgac.database import db