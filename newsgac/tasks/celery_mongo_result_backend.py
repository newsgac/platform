import json
import redis
from datetime import datetime
from uuid import UUID
from bson.errors import InvalidDocument
from celery import states
from celery.backends.mongodb import MongoBackend
from kombu.exceptions import EncodeError

from newsgac import config
from .models import TrackedTask


class ExtendedMongoBackend(MongoBackend):
    def add_to_chord(self, chord_id, result):
        pass

    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):
        try:

            client = redis.Redis(host=config.redis_host, port=config.redis_port)
            client.publish("celery_task_" + task_id, json.dumps({'id': task_id, 'state': state, 'result': result, 'traceback': traceback}))

            #  Do an update query, because race conditions can happen otherwise.
            query = {
                '$set': dict(
                    status=state,
                    date_started=datetime.now(),
                    date_done=datetime.now() if state in [states.FAILURE, states.SUCCESS, states.REVOKED] else None,
                    traceback=traceback,
                    **{'result.%s' % key: result[key] for key in result or {}}
                )
            }
            n_updated = TrackedTask.objects.raw({'_id': UUID(task_id)}).update(query)
        except InvalidDocument as exc:
            raise EncodeError(exc)

        return result
