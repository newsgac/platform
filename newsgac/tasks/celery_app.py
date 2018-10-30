from celery import Celery, Task
from kombu.serialization import register

from newsgac import config
from newsgac.common.json_encoder import _dumps, _loads

from newsgac import database

register('myjson', _dumps, _loads, content_type='application/x-myjson', content_encoding='utf-8')


celery_app = Celery(
    'newsgac.tasks',
    broker=config.redis_url,
    # backend='rpc://',
    include=[
        'newsgac.tasks',
        'newsgac.data_sources.tasks',
        'newsgac.nlp_tools.tasks',
        'newsgac.pipelines.tasks',
        'newsgac.ace.tasks',
        'newsgac.cached_views.tasks',
    ],
)

class DefaultTask(Task):
    ignore_result = True

class ResultTask(Task):
    ignore_result = False


celery_app.Task = DefaultTask
celery_app.conf.broker_connection_timeout = 1
celery_app.conf.task_always_eager = config.celery_eager
celery_app.conf.task_ignore_result = False
celery_app.conf.task_track_started = True
celery_app.conf.result_backend = config.redis_url
celery_app.conf.accept_content = ['myjson', 'pickle']
celery_app.conf.task_serializer = 'myjson'
celery_app.conf.result_serializer = 'myjson'
celery_app.conf.task_routes = {
    'newsgac.nlp_tools.tasks.frog_process': {'queue': 'frog'}
}
# celery_app.conf.mongodb_backend_settings = {
#     'host': config.mongo_host,
#     'port': config.mongo_port,
#     'database': config.mongo_database_name,
    # 'taskmeta_collection': 'celery_tasks',
# }
from newsgac.database import db