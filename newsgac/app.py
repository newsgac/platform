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
from newsgac.pipelines.views import pipeline_blueprint
from newsgac.learners.views import learner_blueprint
from newsgac.models.tasks.views import task_blueprint
from newsgac.models.ace.views import ace_blueprint

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(experiment_blueprint, url_prefix="/experiments")
app.register_blueprint(data_source_blueprint, url_prefix="/data_sources")
app.register_blueprint(pipeline_blueprint, url_prefix="/pipelines")
app.register_blueprint(learner_blueprint, url_prefix="/learners")
app.register_blueprint(task_blueprint, url_prefix="/tasks")
app.register_blueprint(ace_blueprint, url_prefix="/ace")

app.json_encoder = _JSONEncoder

@app.context_processor
def inject_bokeh_js_css():
    from bokeh.resources import CDN
    return dict(bokeh_js_css=CDN)


@app.context_processor
def inject_pymodm_fields():
    from pymodm import fields
    return dict(pymodm_fields=fields)

@app.template_filter('datetime')
def _format_datetime(date):
    return date.strftime('%d-%m-%Y %H:%m')

@app.template_filter('dict_string')
def _format_dict_string(dict_val):
    return ', '.join("%s=%s" % (key, val) for (key, val) in dict_val.iteritems() if key != '_cls')

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
