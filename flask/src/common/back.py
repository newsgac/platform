import functools
from src.app import app
from flask import session, redirect, current_app, request, url_for

# This snippet is in public domain.
# However, please retain this link in your sources:
# http://flask.pocoo.org/snippets/120/
# Danya Alexeyevsky

class back(object):
    with app.app_context():
        cfg = current_app.config.get
        cookie = cfg('REDIRECT_BACK_COOKIE', 'back')
        # default_view = cfg('REDIRECT_BACK_DEFAULT', 'experiments.index')
        default_view = cfg('REDIRECT_BACK_DEFAULT', 'home')

    @staticmethod
    def anchor(func, cookie=cookie):
        @functools.wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.url
            return func(*args, **kwargs)
        return result

    @staticmethod
    def url(default=default_view, cookie=cookie):
        return session.get(cookie, url_for(default))

    @staticmethod
    def redirect(default=default_view, cookie=cookie):
        return redirect(back.url(default, cookie))