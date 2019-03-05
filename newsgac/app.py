#!/usr/bin/env python
import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_dsn = os.environ.get('SENTRY_DSK', None)
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()]
    )

from flask import Flask, render_template

from newsgac import config
from newsgac.common.filters import load_filters
from newsgac.common.json_encoder import _JSONEncoder

from newsgac.users.views import user_blueprint
from newsgac.data_sources.views import data_source_blueprint
from newsgac.pipelines.views import pipeline_blueprint
from newsgac.tasks.views import task_blueprint
from newsgac.ace.views import ace_blueprint
from newsgac import database

__author__ = 'abilgin'

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route('/')
def home():
    return render_template('home.html')


app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(data_source_blueprint, url_prefix="/data_sources")
app.register_blueprint(pipeline_blueprint, url_prefix="/pipelines")
app.register_blueprint(task_blueprint, url_prefix="/tasks")
app.register_blueprint(ace_blueprint, url_prefix="/ace")

app.json_encoder = _JSONEncoder

load_filters(app)

if config.environment in [config.Env.local, config.Env.localdocker]:
    import time
    last_time = time.time()

    def time_measure():
        global last_time
        print (time.time() - last_time)
        last_time = time.time()

    app.jinja_env.globals.update(time_measure=time_measure)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=config.flask_port,
        debug=app.config['DEBUG']
    )
