from celery import Task

from newsgac.models.tasks.tracked_task import TrackedTask


class CeleryTrackedTask(Task):
    def apply_async(self, args=None, kwargs=None, **options):
        task = TrackedTask.create(self.name, args, kwargs)
        task.backend = 'celery'
        task.save_to_db()
        return super(CeleryTrackedTask, self).apply_async(args, kwargs, headers={'tracked_task_id': task._id}, **options)
