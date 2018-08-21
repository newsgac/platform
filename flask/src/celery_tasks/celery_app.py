from celery import Celery
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))


from src import config


celery_app = Celery('src.celery_tasks',
                    broker=config.rabbitmq_url,  # use it when dockerized
                    backend='rpc://',
                    include=['src.celery_tasks.tasks'],
                    task_always_eager=config.celery_eager
                    )
