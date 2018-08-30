from celery import Task
from flask import session

# This class injects flask session['email'] into the task header
class UserTask(Task):
    def apply_async(self, *args, **kwargs):
        return super(UserTask, self).apply_async(*args, headers={'user_email': session.get('email', None)}, **kwargs)
