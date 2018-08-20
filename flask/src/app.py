#!/usr/bin/env python
from flask import Flask, render_template

__author__ = 'abilgin'

app = Flask(__name__)
app.secret_key = "newsgacdev123"
app.__setattr__("DOCKER_RUN", False)

@app.route('/')
def home():
    return render_template('home.html')

from src.models.users.views import user_blueprint
from src.models.experiments.views import experiment_blueprint
from src.models.data_sources.views import data_source_blueprint
app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(experiment_blueprint, url_prefix="/experiments")
app.register_blueprint(data_source_blueprint, url_prefix="/data_sources")
