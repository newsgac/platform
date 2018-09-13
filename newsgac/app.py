#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, render_template
from newsgac import config
from newsgac.database import db
from newsgac.common.json_encoder import _JSONEncoder

__author__ = 'abilgin'

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route('/')
def home():
    return render_template('home.html')

from newsgac.users.views import user_blueprint
from newsgac.models.experiments.views import experiment_blueprint
from newsgac.data_sources.views import data_source_blueprint
from newsgac.pre_processors.views import pre_processor_blueprint
from newsgac.models.tasks.views import task_blueprint
from newsgac.models.ace.views import ace_blueprint

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(experiment_blueprint, url_prefix="/experiments")
app.register_blueprint(data_source_blueprint, url_prefix="/data_sources")
app.register_blueprint(pre_processor_blueprint, url_prefix="/pre_processors")
app.register_blueprint(task_blueprint, url_prefix="/tasks")
app.register_blueprint(ace_blueprint, url_prefix="/ace")

app.json_encoder = _JSONEncoder

@app.context_processor
def inject_bokeh_js_css():
    from bokeh.resources import CDN
    return dict(bokeh_js_css=CDN)


@app.template_filter('datetime')
def _format_datetime(date):
    return date.strftime('%d-%m-%Y %H:%m')


if config.environment in [config.Env.local, config.Env.localdocker]:
    import time
    last_time = time.time()

    def time_measure():
        global last_time
        print time.time() - last_time
        last_time = time.time()

    app.jinja_env.globals.update(time_measure=time_measure)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=config.flask_port,
        debug=app.config['DEBUG']
    )
