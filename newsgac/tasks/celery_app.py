import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from celery import Celery
from newsgac.tasks.celery_tracked_task import CeleryTrackedTask
from newsgac import config
from kombu.serialization import register
from newsgac.common.json_encoder import _dumps, _loads


register('myjson', _dumps, _loads, content_type='application/x-myjson', content_encoding='utf-8')

celery_app = Celery('newsgac.tasks',
                    broker=config.rabbitmq_url,
                    backend='rpc://',
                    include=['newsgac.tasks', 'newsgac.data_sources.tasks', 'newsgac.tasks.tasks'],
                    task_cls=CeleryTrackedTask
                    )

celery_app.conf.broker_connection_timeout = 1
celery_app.conf.task_always_eager = config.celery_eager
celery_app.conf.task_ignore_result = False
celery_app.conf.task_track_started = True
celery_app.conf.result_backend = 'newsgac.tasks.celery_mongo_result_backend.ExtendedMongoBackend'
celery_app.conf.accept_content = ['myjson']
celery_app.conf.task_serializer = 'myjson'
celery_app.conf.result_serializer = 'myjson'
celery_app.conf.mongodb_backend_settings = {
    'host': config.mongo_host,
    'port': config.mongo_port,
    'database': config.mongo_database_name,
    'taskmeta_collection': 'celery_tasks',
}
from newsgac.database import db