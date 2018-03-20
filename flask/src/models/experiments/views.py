from __future__ import absolute_import

from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect

from src.app import app
from src.models.configurations.configuration_svc import ConfigurationSVC
from src.common.back import back
from src.models.configurations.configuration_dt import ConfigurationDT
from src.models.experiments.experiment import Experiment, ExperimentDT, ExperimentSVC
import src.models.users.decorators as user_decorators
import src.models.configurations.errors as ConfigurationErrors
from src.models.data_sources.data_source import DataSource
from src.celery_tasks.tasks import run_exp, del_exp
import time
from bokeh.resources import INLINE

from src.visualisation.comparison import ExperimentComparator
from src.visualisation.resultvisualiser import ResultVisualiser

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
    # get the list of data sources of the user
    existing_data_source_titles = DataSource.get_titles_by_user_email(user_email=session['email'], processed=True)

    if request.method == 'POST':
        configuration = ConfigurationDT(user_email=session['email'], form=request.form)
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
                return render_template('experiments/new_experiment_dt.html', request=request.form)

    return render_template('experiments/new_experiment_dt.html', ds_titles_from_db=existing_data_source_titles)


@experiment_blueprint.route('/new_svm', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_svm():
    # get the list of processed data sources of the user
    existing_data_source_titles = DataSource.get_titles_by_user_email(user_email=session['email'], processed=True)

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
                return render_template('experiments/new_experiment_svm.html', request=request.form)

    return render_template('experiments/new_experiment_svm.html', ds_titles_from_db=existing_data_source_titles)


@experiment_blueprint.route('/new_ft', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_ft():
    #TODO FastText can be used with raw data (DataSource.get_titles_by_user_email(user_email=session['email'], processed=False))
    return render_template('underconstruction.html')


@experiment_blueprint.route('/new_dl', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_dl():
    #TODO Deep Learning can be used with raw data (DataSource.get_titles_by_user_email(user_email=session['email'], processed=False))
    return render_template('underconstruction.html')


@experiment_blueprint.route('/<string:experiment_id>')
@user_decorators.requires_login
def get_experiment_page(experiment_id):
    # return the experiment page with the type code
    experiment = Experiment.get_by_id(experiment_id)
    if experiment.type == "SVC":
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
    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = run_exp.delay(experiment_id)
    else:
        # without celery
        exp = Experiment.get_by_id(experiment_id)
        if exp.type == "SVC":
            ExperimentSVC.get_by_id(experiment_id).run_svc()
        elif exp.type == "DT":
            ExperimentDT.get_by_id(experiment_id).run_dt()

    time.sleep(0.5)
    return redirect(url_for('.get_experiment_page', experiment_id=experiment_id))


@experiment_blueprint.route('/visualise/<string:experiment_id>')
@user_decorators.requires_login
def visualise_results(experiment_id):
    experiment = Experiment.get_by_id(experiment_id)
    results = experiment.get_results()
    p, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results, title="")

    return render_template('experiments/results.html',
                           experiment=experiment,
                           results=results,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')


@experiment_blueprint.route('/predict/<string:experiment_id>', methods=['GET', 'POST'])
@user_decorators.requires_login
def predict(experiment_id):
    experiment = Experiment.get_by_id(experiment_id)

    if request.method == 'POST':
        sorted_prediction_results = experiment.predict(request.form['raw_text'])
        try:
            plot, script, div = ResultVisualiser.visualise_sorted_probabilities_for_raw_text_prediction(sorted_prediction_results,
                                                                                                        experiment.display_title)
            return render_template('experiments/prediction.html',
                           experiment=experiment, request = request.form,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')
        except Exception as e:
            flash("Something went wrong: " + e.message, 'error')
            return render_template('experiments/prediction.html', experiment=experiment, request = request.form)

    return render_template('experiments/prediction.html', experiment=experiment)

@experiment_blueprint.route('/features_visualisation/<string:experiment_id>')
@user_decorators.requires_login
def visualise_features(experiment_id):
    f_weights = None
    experiment = Experiment.get_by_id(experiment_id)
    if experiment.type == "SVC":
        f_weights = ExperimentSVC.get_by_id(experiment_id).get_features_weights()

    if f_weights is not None:
        p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights, main_title=experiment.display_title)

        return render_template('experiments/features.html',
                               experiment=experiment,
                               plot_script=script, plot_div=div, js_resources=INLINE.render_js(),
                               css_resources=INLINE.render_css(),
                               mimetype='text/html')

    return render_template('experiments/features.html', experiment=experiment)


@experiment_blueprint.route('/prediction_overview',  methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def user_experiments_overview_for_prediction():
    # call overview method with the finished experiments that belong to the user
    finished_experiments = Experiment.get_finished_user_experiments(session['email'])
    comparator = ExperimentComparator(finished_experiments)

    if request.method == 'POST':
        try:
            script, div = comparator.visualise_prediction_comparison(request.form['raw_text'])
            return render_template('experiments/prediction_overview.html',
                           request = request.form,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')
        except Exception as e:
            print e.message
            return render_template('experiments/prediction_overview.html', request=request.form)

    return render_template('experiments/prediction_overview.html')


@experiment_blueprint.route('/overview',  methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def user_experiments_overview():
    if not session['email']:
        return redirect(url_for("experiments.public_overview"))

    test_articles = []
    processed_data_source_list = []
    used_data_source_ids_by_user = Experiment.get_used_data_sources_for_user(user_email=session['email'])

    for ds_id in used_data_source_ids_by_user:
        processed_data_source_list.append(DataSource.get_by_id(ds_id))

    if request.method == 'POST':
        # try:

        if request.form['data_source'] == "ALL":
            # call overview method with the finished experiments that belong to the user
            finished_experiments = Experiment.get_finished_user_experiments(user_email=session['email'])
        elif request.form['data_source'] == "":
            finished_experiments = Experiment.get_finished_user_experiments_using_data_id(user_email=session['email'],
                                                                                          ds_id=None)
        else:
            finished_experiments = Experiment.get_finished_user_experiments_using_data_id(user_email=session['email'],
                                                                                          ds_id=request.form['data_source'])

        comparator = ExperimentComparator(finished_experiments)

        # get the test articles
        test_articles = comparator.retrieveTestArticles()
        tabular_data_dict, combinations = comparator.generateAgreementOverview(test_articles)


        script, div = comparator.performComparison()
        script_cm, div_cm = comparator.combineHeatMapPlotsForAllExperiments()
        script.append(script_cm)
        div.append(div_cm)

        return render_template('experiments/overview.html', plot_scripts=script, plot_divs=div,
                       js_resources=INLINE.render_js(), data_sources_db=processed_data_source_list,
                       articles=test_articles, tabular_data_dict=tabular_data_dict,
                       combinations=combinations,
                       css_resources=INLINE.render_css(), mimetype='text/html')
        # except Exception as e:
        #     flash(e.message, 'error')
        #     return render_template('experiments/overview.html', data_sources_db=processed_data_source_list,
        #                            request=request.form)

    return render_template('experiments/overview.html', data_sources_db=processed_data_source_list)


@experiment_blueprint.route('/public_prediction_overview', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def public_experiments_overview_for_prediction():
    # call overview method with the finished public experiments
    experiments = Experiment.get_public_experiments()
    comparator = ExperimentComparator(experiments)

    if request.method == 'POST':
        try:
            script, div = comparator.visualise_prediction_comparison(request.form['raw_text'])
            return render_template('experiments/prediction_overview.html',
                           request = request.form,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')
        except Exception as e:
            print e.message
            return render_template('experiments/prediction_overview.html', request=request.form)

    return render_template('experiments/prediction_overview.html')


@experiment_blueprint.route('/public_overview', methods=['GET', 'POST'])
@back.anchor
def public_overview():
    processed_data_source_list = DataSource.get_processed_datasets()

    if request.method == 'POST':
        try:

            if request.form['data_source'] == "ALL":
                # call overview method with the finished experiments that belong to the user
                experiments = Experiment.get_public_experiments()
            elif request.form['data_source'] == "":
                experiments = Experiment.get_public_experiments_using_data_id(ds_id=None)
            else:
                experiments = Experiment.get_public_experiments_using_data_id(ds_id=request.form['data_source'])
            # call overview method with the public experiments

            comparator = ExperimentComparator(experiments)
            script, div = comparator.performComparison()
            script_cm, div_cm = comparator.combineHeatMapPlotsForAllExperiments()
            script.append(script_cm)
            div.append(div_cm)

            return render_template('experiments/overview.html', plot_scripts=script, plot_divs=div,
                                   js_resources=INLINE.render_js(), data_sources_db=processed_data_source_list,
                                   css_resources=INLINE.render_css(), mimetype='text/html')

        except Exception as e:
            flash(e.message, 'error')
            return render_template('experiments/overview.html', data_sources_db=processed_data_source_list,
                                   request=request.form)

    return render_template('experiments/overview.html', data_sources_db=processed_data_source_list)


@experiment_blueprint.route('/delete/<string:experiment_id>')
@user_decorators.requires_login
def delete_experiment(experiment_id):
    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = del_exp.delay(experiment_id)
    else:
        # without celery
        exp = Experiment.get_by_id(experiment_id)
        if exp.type == "SVC":
            ExperimentSVC.get_by_id(experiment_id).delete()
        elif exp.type == "DT":
            ExperimentDT.get_by_id(experiment_id).delete()

    time.sleep(0.5)
    return back.redirect()


