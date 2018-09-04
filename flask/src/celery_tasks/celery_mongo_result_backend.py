from datetime import datetime

from bson.errors import InvalidDocument
from celery import states
from celery.backends.mongodb import MongoBackend
from kombu.exceptions import EncodeError

from src.models.tasks.tracked_task import TrackedTask


class ExtendedMongoBackend(MongoBackend):
    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):

        if state == states.STARTED:
            try:
                task = TrackedTask.get_by_id(request.tracked_task_id)
                task.status = state
                task.results.append({
                    '_id': task_id,
                    'status': state,
                    'children': self.encode(
                        self.current_task_children(request),
                    ),
                    'date_started': datetime.utcnow(),
                    'worker_name': result.get('hostname'),
                    'worker_pid': result.get('pid'),
                    'date_done': None,
                    'result': None,
                    'traceback': None,
                })
                task.save_to_db()
            except InvalidDocument as exc:
                raise EncodeError(exc)

        else:
            # `request` is not available when task.update_state() is triggered
            task = TrackedTask.find_one({'results._id': task_id})
            if state in [states.FAILURE, states.SUCCESS]:
                task.date_done = datetime.utcnow()
                task.status = state
            else:
                task.status = states.STARTED

            for task_result in task.results:
                if task_result['_id'] == task_id:
                    task_result.update({
                        'status': state,
                        'result': result,
                        'traceback': traceback,
                        'date_done': datetime.utcnow(),
                    })
            task.save_to_db()

        return result
