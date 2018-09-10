from datetime import datetime
from uuid import UUID

from bson.errors import InvalidDocument
from celery import states
from celery.backends.mongodb import MongoBackend
from kombu.exceptions import EncodeError

from .models import TrackedTask


class ExtendedMongoBackend(MongoBackend):
    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):
        try:
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
