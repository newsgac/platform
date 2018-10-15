from functools import wraps

from flask import session, flash, url_for, request, Markup
from werkzeug.utils import redirect

__author__ = 'abilgin'


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            flash(Markup('You need to be logged in for this page. Please login below.'+
                         ' Don\'t have an account? <ws href="/users/register" class="alert-link">Register here.</ws>'), 'warning')
            return redirect(url_for('users.login_user', next=request.path))
        return f(*args, **kwargs)

    return decorated_function


def requires_no_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session.keys() and session['email'] is not None:
            flash('You are already logged in.', 'info')
            return redirect(url_for("experiments.user_experiments"))
        return f(*args, **kwargs)

    return decorated_function

# def requires_user_admin_permissions(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         experiment = Experiment.get_by_id(kwargs['experiment_id'])
#         if session['email'] != experiment.user_email:
#             flash('You can only do this for experiments created by you.', 'warning')
#             return redirect(request.referrer)
#             # return redirect(url_for('users.login_user', message=""))
#         return f(*args, **kwargs)
#
#     return decorated_function

