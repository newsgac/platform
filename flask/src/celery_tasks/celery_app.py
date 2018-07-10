from celery import Celery

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

celery_app = Celery('src.celery_tasks',
                CELERY_TASK_SERIALIZER = 'pickle',
             broker='amqp://newsgac:1234@rabbit//',   # use it when dockerized
             # broker='amqp://newsgac:1234@localhost/newsgac_vhost',
             backend='rpc://',
             include=['src.celery_tasks.tasks'])