import uuid

from celery import Task

from newsgac.tasks.models import TrackedTask, Status


class CeleryTrackedTask(Task):
    def apply_async(self, args=None, kwargs=None, **options):
        task_id = options.get('task_id', str(uuid.uuid4()))
        task = TrackedTask(
            _id=task_id,
            name=self.name,
            status=Status.QUEUED,
            task_args=args or [],
            task_kwargs=kwargs or {},
            backend='celery',
            result={}
        )
        try:
            task.save()
        except Exception as e:
            raise
        task_eager_result = super(CeleryTrackedTask, self).apply_async(args, kwargs, task_id=task_id, **options)

        # task.refresh_from_db()
        # task.children = task_eager_result.children or []
        # task.parent = task_eager_result.parent
        # task.save()

        return task_eager_result
