from celery import current_task


def report_progress(name, value):
    if not current_task:
        return
        # raise EnvironmentError('Not in a celery task')
    if getattr(current_task, 'progress', None) is None:
        setattr(current_task, 'progress', [])
    progress = getattr(current_task, 'progress')
    try:
        current = [x for x in progress if x['name'] == name][0]
    except IndexError:
        current = {
            'name': name,
            'progress': 0
        }
        progress.append(current)
    current['progress'] = value
    current_task.update_state(state='PROCESSING', meta={'progress': progress})
