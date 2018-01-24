from __future__ import absolute_import

from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect

from data_engineering.postprocessing import ExperimentComparator
from models.configurations.configuration_svc import ConfigurationSVC
from src.common.back import back
from models.configurations.configuration_dt import ConfigurationDT
from src.models.experiments.experiment import Experiment, ExperimentDT, ExperimentSVC
import src.models.users.decorators as user_decorators
import src.models.configurations.errors as ConfigurationErrors
# from src.celery_tasks.tasks import run_exp, del_exp
import time
from bokeh.resources import INLINE

__author__ = 'abilgin'

experiment_blueprint = Blueprint('experiments', __name__)

@experiment_blueprint.route('/public')
@back.anchor
def index():
    return render_template('experiments/public.html', experiments = Experiment.get_public_experiments())

@experiment_blueprint.route('/')
@user_decorators.requires_login
@back.anchor
def user_experiments():
    return render_template("experiments/experiments.html", experiments = Experiment.get_by_user_email(session['email']))

@experiment_blueprint.route('/new_dt', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_dt():
    if request.method == 'POST':
        configuration = ConfigurationDT(user_email= session['email'], form = request.form)
        try:
            if ConfigurationDT.is_config_unique(configuration):
                configuration.save_to_db()
                display_title = request.form['experiment_display_title']
                public_flag = 'public_flag' in request.form
                experiment = ExperimentDT(user_email=session['email'], display_title=display_title, public_flag=public_flag,
                                        **dict(configuration=configuration))
                experiment.save_to_db()
                return redirect(url_for('.user_experiments'))
        except ConfigurationErrors.ConfigAlreadyExistsError as e:
                error = e.message
                flash(error, 'error')

    return render_template('experiments/new_experiment_dt.html')

@experiment_blueprint.route('/new_svm', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_svm():
    if request.method == 'POST':
        configuration = ConfigurationSVC(user_email= session['email'], form = request.form)
        try:
            if ConfigurationSVC.is_config_unique(configuration):
                configuration.save_to_db()
                display_title = request.form['experiment_display_title']
                public_flag = 'public_flag' in request.form
                experiment = ExperimentSVC(user_email=session['email'], display_title=display_title, public_flag=public_flag,
                                        **dict(configuration=configuration))
                experiment.save_to_db()
                return redirect(url_for('.user_experiments'))
        except ConfigurationErrors.ConfigAlreadyExistsError as e:
                error = e.message
                flash(error, 'error')

    return render_template('experiments/new_experiment_svm.html')

@experiment_blueprint.route('/new_ft', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_ft():
    #TODO FastText
    return render_template('underconstruction.html')

@experiment_blueprint.route('/new_dl', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_dl():
    #TODO Deep Learning
    return render_template('underconstruction.html')

@experiment_blueprint.route('/<string:experiment_id>')
@user_decorators.requires_login
def get_experiment_page(experiment_id):
    # return the experiment page with the type code
    experiment = Experiment.get_by_id(experiment_id)
    if experiment.type == "SVC":
        # if experiment.trained_model_handler is not None:
        #     ExperimentSVC.get_by_id(experiment_id).predict("")
        return render_template('experiments/experiment_svm.html', experiment=experiment)
    elif experiment.type == "DT":
        return render_template('experiments/experiment_dt.html', experiment=experiment)
    elif experiment.type == "DL":
        return render_template('experiments/experiment_dl.html', experiment=experiment)
    else:
        return render_template('experiments/experiment_ft.html', experiment=experiment)

@experiment_blueprint.route('/train/<string:experiment_id>')
@user_decorators.requires_login
def run_experiment(experiment_id):
    # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
    # task = run_exp.delay(experiment_id)
    # without celery
    exp_type = Experiment.get_by_id(experiment_id).type
    if exp_type == "SVC":
        ExperimentSVC.get_by_id(experiment_id).start_running()
    elif exp_type == "DT":
        ExperimentDT.get_by_id(experiment_id).start_running()
    time.sleep(0.5)
    return redirect(url_for('.get_experiment_page', experiment_id=experiment_id))

@experiment_blueprint.route('/visualise/<string:experiment_id>')
@user_decorators.requires_login
def visualise_results(experiment_id):
    experiment = Experiment.get_by_id(experiment_id)

    results = experiment.get_results()
    script, div = results.visualise_confusion_matrix(True)
    return render_template('experiments/results.html',
                           experiment=experiment,
                           results=results,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')

@experiment_blueprint.route('/overview',  methods=['GET'])
@user_decorators.requires_login
@back.anchor
def user_experiments_overview():
    # call overview method with the experiments that belong to the user
    experiments = Experiment.get_by_user_email(session['email'])
    comparator = ExperimentComparator(experiments)
    script, div = comparator.performComparison()

    return render_template('experiments/overview.html', plot_script=script, plot_div=div,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css(), mimetype='text/html')

@experiment_blueprint.route('/public_overview')
@back.anchor
def public_overview():
    # call overview method with the public experiments
    experiments = Experiment.get_public_experiments()
    comparator = ExperimentComparator(experiments)
    script, div = comparator.performComparison()

    return render_template('experiments/overview.html', plot_script=script, plot_div=div,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css(), mimetype='text/html')


@experiment_blueprint.route('/delete/<string:experiment_id>')
@user_decorators.requires_login
def delete_experiment(experiment_id):
    # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
    # task = del_exp.delay(experiment_id)
    # without celery
    exp_type = Experiment.get_by_id(experiment_id).type
    if exp_type == "SVC":
        ExperimentSVC.get_by_id(experiment_id).delete()
    elif exp_type == "DT":
        ExperimentDT.get_by_id(experiment_id).delete()
    time.sleep(0.5)
    return back.redirect()


