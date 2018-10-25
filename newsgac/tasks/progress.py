import redis
from celery import current_task
from flask import json

from newsgac import config

task_id = None
def report_progress(name, value):
    if task_id:
        client = redis.Redis(host=config.redis_host, port=config.redis_port)
        client.publish("celery_task_" + task_id,
            json.dumps({
                'id': task_id,
                'state': 'PROCESSING',
                'result': {
                    'progress': [{
                        'name': name,
                        'progress': value
                    }]
                },
                'traceback': None
            })
        )
        return

    if not current_task:
        return

    if getattr(current_task, 'progress', None) is None:
        setattr(current_task, 'progress', [])
    progress = getattr(current_task, 'progress')
    try:
        current = [x for x in progress if x['name'] == name][0]
    except IndexError:
        current = {
            'name': name,
            'progress': 0
        }
        progress.append(current)
    current['progress'] = value
    current_task.update_state(state='PROCESSING', meta={'progress': progress})
