import hashlib

from flask import render_template

from newsgac.tasks.models import Status
from pymodm.errors import DoesNotExist

from newsgac.cached_views.models import CachedView
from newsgac.cached_views.tasks import save_view_task_result_error


def cached_view(template, view_name, task, args, kwargs):
    hash = hashlib.sha1('%s.%s.%s' % (view_name, args.__repr__(), kwargs.__repr__())).hexdigest()
    try:
        cache = CachedView.objects.get({'hash': hash})
    except DoesNotExist:
        cache = CachedView()
        cache.hash = hash
        cache.task.set_started()
        cache.save()

        task.s(cache._id, *args, **kwargs).on_error(save_view_task_result_error.s(cache._id)).apply_async(),

    if cache.task.status == Status.SUCCESS:
        return render_template(template, **cache.data)

    return 'STARTED/FAILURE'
