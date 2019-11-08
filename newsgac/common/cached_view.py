import hashlib

from flask import render_template, flash

from newsgac.tasks.models import Status
from pymodm.errors import DoesNotExist

from newsgac.cached_views.models import CachedView
from newsgac.cached_views.tasks import save_view_task_result_error

from flask import Markup, request

def generate_view_data(hash, task, args, kwargs):
    cache = CachedView()
    cache.hash = hash
    cache.task.set_started()
    cache.save()

    task.s(cache._id, *args, **kwargs).on_error(save_view_task_result_error.s(cache._id)).apply_async()

    return cache


def cached_view(template, view_name, task, args, kwargs):
    to_hash = '%s.%s.%s' % (view_name, args.__repr__(), kwargs.__repr__())
    hash = hashlib.sha1(to_hash.encode('ascii')).hexdigest()
    try:
        cache = CachedView.objects.get({'hash': hash})
    except DoesNotExist:
        cache = generate_view_data(hash, task, args, kwargs)

    if request.args.get('refresh') == "1":
        cache.delete()
        cache = generate_view_data(hash, task, args, kwargs)

    if cache.task.status == Status.SUCCESS:
        flash(Markup('<a href="?refresh=1">This page has been cached. Click here to regenerate</a>'), 'info')
        return render_template(template, **cache.data.get())

    if cache.task.status == Status.STARTED:
        return render_template(
            'cached_views/started.html',
            cache=cache
        )

    if cache.task.status == Status.FAILURE:
        return render_template(
            'cached_views/failure.html',
            cache=cache
        )
