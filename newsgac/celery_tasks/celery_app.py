import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from celery import Celery
from newsgac.celery_tasks.celery_tracked_task import CeleryTrackedTask
from newsgac import config

celery_app = Celery('newsgac.celery_tasks',
                    broker=config.rabbitmq_url,
                    backend='rpc://',
                    include=['newsgac.celery_tasks.tasks', 'newsgac.data_sources.tasks'],
                    task_cls=CeleryTrackedTask
                    )

celery_app.conf.task_always_eager = config.celery_eager
celery_app.conf.task_ignore_result = False
celery_app.conf.task_track_started = True
celery_app.conf.result_backend = 'newsgac.celery_tasks.celery_mongo_result_backend.ExtendedMongoBackend'
celery_app.conf.mongodb_backend_settings = {
    'host': config.mongo_host,
    'port': config.mongo_port,
    'database': config.mongo_database_name,
    'taskmeta_collection': 'celery_tasks',
}
