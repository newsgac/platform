from datetime import datetime

from bson.errors import InvalidDocument
from celery import states
from celery.backends.mongodb import MongoBackend
from kombu.exceptions import EncodeError


class ExtendedMongoBackend(MongoBackend):
    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):

        if state == states.STARTED:
            meta = {
                '_id': task_id,
                'user_email': getattr(request, 'user_email', None),
                'args': getattr(request, 'args', []),
                'status': state,
                # 'request': request.__dict__,
                'task_name': getattr(request, 'task', None),
                'children': self.encode(
                    self.current_task_children(request),
                ),
                'date_started': datetime.utcnow(),
                'worker_name': result.get('hostname'),
                'worker_pid': result.get('pid'),
                'date_done': None,
                'result': None,
                'traceback': None,
            }
            try:
                self.collection.save(meta)
            except InvalidDocument as exc:
                raise EncodeError(exc)

        else:
            # `request` is not available when task.update_state() is triggered
            self.collection.update_one({'_id': task_id}, {'$set': {
                'status': state,
                'result': result,
                'traceback': traceback,
                'date_done': datetime.utcnow(),
            }})

        return result
