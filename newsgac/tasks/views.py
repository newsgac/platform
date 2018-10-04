from flask import Blueprint, session, jsonify
from newsgac.common.back import back
import newsgac.users.view_decorators as user_decorators
from newsgac.tasks.models import TrackedTask

__author__ = 'tom'

task_blueprint = Blueprint('tasks', __name__)

@task_blueprint.route('/')
@user_decorators.requires_login
@back.anchor
def user_tasks():
    return jsonify(TrackedTask.objects.all())
