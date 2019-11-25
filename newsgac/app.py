#!/usr/bin/env python
import logging

from bokeh.embed import components
from bokeh.plotting import figure
from flask import Flask, render_template

from newsgac import config
from newsgac.common.filters import load_filters
from newsgac.common.json_encoder import _JSONEncoder
from newsgac.stop_words.views import stop_words_blueprint

from newsgac.users.views import user_blueprint
from newsgac.data_sources.views import data_source_blueprint
from newsgac.pipelines.views import pipeline_blueprint
from newsgac.tasks.views import task_blueprint
from newsgac.ace.views import ace_blueprint

__author__ = 'abilgin'


logger = logging.getLogger(__name__)


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
app.register_blueprint(stop_words_blueprint, url_prefix="/stop_words")

app.json_encoder = _JSONEncoder

load_filters(app)

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=config.flask_port,
        debug=app.config['DEBUG']
    )
