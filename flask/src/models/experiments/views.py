from __future__ import absolute_import
from __future__ import division

from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect

import src.data_engineering.data_io as DataIO
from src.models.configurations.configuration_svc import ConfigurationSVC
from src.common.back import back
from src.database import DATABASE
from src.models.configurations.configuration_rf import ConfigurationRF
from src.models.configurations.configuration_xgb import ConfigurationXGB
from src.models.configurations.configuration_nb import ConfigurationNB
from src.models.experiments.experiment import Experiment
from src.models.experiments.experiment_xgb import ExperimentXGB
from src.models.experiments.experiment_nb import ExperimentNB
from src.models.experiments.experiment_rf import ExperimentRF
from src.models.experiments.experiment_svc import ExperimentSVC
import src.models.users.decorators as user_decorators
import src.models.configurations.errors as ConfigurationErrors
from src.models.data_sources.data_source import DataSource
from src.celery_tasks.tasks import run_exp, del_exp, predict_exp, predict_overview, predict_overview_public
import time
from bokeh.embed import components
from bokeh.layouts import gridplot

from src.models.experiments.factory import get_experiment_by_id
from src.visualisation.comparison import ExperimentComparator
from src.visualisation.resultvisualiser import ResultVisualiser

from decimal import *

from src import config

getcontext().prec = 2

__author__ = 'abilgin'

experiment_blueprint = Blueprint('experiments', __name__)


@experiment_blueprint.route('/public')
@back.anchor
def index():
    return render_template('experiments/public.html', experiments = Experiment.get_public_experiments())


@experiment_blueprint.route('/user')
@user_decorators.requires_login
@back.anchor
def user_experiments():
    return render_template("experiments/experiments.html", experiments = Experiment.get_by_user_email(session['email']))


@experiment_blueprint.route('/new_nb', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_nb():
    # get the list of processed data sources of the user for only TF-IDF representation
    existing_data_source_titles = DataSource.get_training_titles_by_user_email(user_email=session['email'], processed=True, tfidf=True)
    manual_feature_dict = DataIO.get_feature_names_with_descriptions()

    if not existing_data_source_titles:
        flash("There are no processed data sources for training, redirecting to data sources page.", 'warning')
        return redirect((url_for('data_sources.user_data_sources')))

    if request.method == 'POST':
        if request.form["data_source"]:
            configuration = ConfigurationNB(user_email= session['email'], form = request.form)
            try:
                if ConfigurationNB.is_config_unique(configuration):
                    configuration.save_to_db()
                    display_title = request.form['experiment_display_title']
                    public_flag = 'public_flag' in request.form
                    experiment = ExperimentNB(user_email=session['email'],
                                               display_title=display_title+" ("+configuration.data_source_title+")",
                                               public_flag=public_flag,
                                            **dict(configuration=configuration))
                    experiment.save_to_db()
                    return redirect(url_for('.user_experiments'))
            except ConfigurationErrors.ConfigAlreadyExistsError as e:
                    error = e.message
                    flash(error, 'error')
                    return render_template('experiments/new_experiment_nb.html', request=request.form,
                                           ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)
        else:
            flash('Please choose a data source!', 'error')
            return render_template('experiments/new_experiment_nb.html', request=request.form, ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)


    return render_template('experiments/new_experiment_nb.html', ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict, request={})

@experiment_blueprint.route('/new_rf', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_rf():
    # get the list of processed data sources of the user
    existing_data_source_titles = DataSource.get_training_titles_by_user_email(user_email=session['email'], processed=True)
    manual_feature_dict = DataIO.get_feature_names_with_descriptions()

    if not existing_data_source_titles:
        flash("There are no processed data sources for training, redirecting to data sources page.", 'warning')
        return redirect((url_for('data_sources.user_data_sources')))

    if request.method == 'POST':
        if request.form["data_source"]:
            configuration = ConfigurationRF(user_email= session['email'], form = request.form)
            try:
                if ConfigurationRF.is_config_unique(configuration):
                    configuration.save_to_db()
                    display_title = request.form['experiment_display_title']
                    public_flag = 'public_flag' in request.form
                    experiment = ExperimentRF(user_email=session['email'],
                                               display_title=display_title+" ("+configuration.data_source_title+")",
                                               public_flag=public_flag,
                                            **dict(configuration=configuration))
                    experiment.save_to_db()
                    return redirect(url_for('.user_experiments'))
            except ConfigurationErrors.ConfigAlreadyExistsError as e:
                    error = e.message
                    flash(error, 'error')
                    return render_template('experiments/new_experiment_rf.html', request=request.form,
                                           ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)
        else:
            flash('Please choose a data source!', 'error')
            return render_template('experiments/new_experiment_rf.html', request=request.form, ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)


    return render_template('experiments/new_experiment_rf.html', ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict, request={})



@experiment_blueprint.route('/new_svc', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_svc():
    # get the list of processed data sources of the user
    existing_data_source_titles = DataSource.get_training_titles_by_user_email(user_email=session['email'], processed=True)
    manual_feature_dict = DataIO.get_feature_names_with_descriptions()

    if not existing_data_source_titles:
        flash("There are no processed data sources for training, redirecting to data sources page.", 'warning')
        return redirect((url_for('data_sources.user_data_sources')))

    if request.method == 'POST':
        if request.form["data_source"]:
            configuration = ConfigurationSVC(user_email= session['email'], form = request.form)
            try:
                if ConfigurationSVC.is_config_unique(configuration):
                    configuration.save_to_db()
                    display_title = request.form['experiment_display_title']
                    public_flag = 'public_flag' in request.form
                    experiment = ExperimentSVC(user_email=session['email'],
                                               display_title=display_title+" ("+configuration.data_source_title+")",
                                               public_flag=public_flag,
                                            **dict(configuration=configuration))
                    experiment.save_to_db()
                    return redirect(url_for('.user_experiments'))
            except ConfigurationErrors.ConfigAlreadyExistsError as e:
                    error = e.message
                    flash(error, 'error')
                    return render_template('experiments/new_experiment_svc.html', request=request.form,
                                           ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)
        else:
            flash('Please choose a data source!', 'error')
            return render_template('experiments/new_experiment_svc.html', request=request.form, ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)


    return render_template('experiments/new_experiment_svc.html', ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict, request={})


@experiment_blueprint.route('/new_xgb', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_experiment_xgb():
    # get the list of processed data sources of the user
    existing_data_source_titles = DataSource.get_training_titles_by_user_email(user_email=session['email'], processed=True)
    manual_feature_dict = DataIO.get_feature_names_with_descriptions()

    if not existing_data_source_titles:
        flash("There are no processed data sources for training, redirecting to data sources page.", 'warning')
        return redirect((url_for('data_sources.user_data_sources')))

    if request.method == 'POST':
        if request.form["data_source"]:
            configuration = ConfigurationXGB(user_email= session['email'], form = request.form)
            try:
                if ConfigurationXGB.is_config_unique(configuration):
                    configuration.save_to_db()
                    display_title = request.form['experiment_display_title']
                    public_flag = 'public_flag' in request.form
                    experiment = ExperimentXGB(user_email=session['email'],
                                               display_title=display_title+" ("+configuration.data_source_title+")",
                                               public_flag=public_flag,
                                            **dict(configuration=configuration))
                    experiment.save_to_db()
                    return redirect(url_for('.user_experiments'))
            except ConfigurationErrors.ConfigAlreadyExistsError as e:
                    error = e.message
                    flash(error, 'error')
                    return render_template('experiments/new_experiment_xgb.html', request=request.form,
                                           ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)
        else:
            flash('Please choose a data source!', 'error')
            return render_template('experiments/new_experiment_xgb.html', request=request.form, ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict)


    return render_template('experiments/new_experiment_xgb.html', ds_titles_from_db=existing_data_source_titles,
                           feature_dict = manual_feature_dict, request={})

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
    experiment = get_experiment_by_id(experiment_id)
    experiment_type_template_map = {
        ExperimentNB.type:  'experiments/experiment_nb.html',
        ExperimentSVC.type: 'experiments/experiment_svc.html',
        ExperimentRF.type:  'experiments/experiment_rf.html',
        ExperimentXGB.type: 'experiments/experiment_xgb.html',
        'DL':               'experiments/experiment_dl.html',
    }
    template = experiment_type_template_map.get(experiment.type, 'experiments/experiment_ft.html')

    return render_template(template, experiment=experiment)


@experiment_blueprint.route('/train/<string:experiment_id>')
@user_decorators.requires_login
def run_experiment(experiment_id):
    task = run_exp.delay(experiment_id)
    time.sleep(0.5)
    return redirect(url_for('.get_experiment_page', experiment_id=experiment_id))


@experiment_blueprint.route('/visualise/<string:experiment_id>')
@user_decorators.requires_login
def visualise_results(experiment_id):
    experiment = get_experiment_by_id(experiment_id)
    results_eval = experiment.get_results_eval()
    results_model = experiment.get_results_model()
    p, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_eval, title="Evaluation", ds_param=0.7)
    p_mod, script_mod, div_mod = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_model, title="Model", ds_param=0.7)

    plots = []
    plots.append(p)
    plots.append(p_mod)
    overview_layout = gridplot(plots, ncols=2)
    script, div = components(overview_layout)

    return render_template('experiments/results.html',
                           experiment=experiment,
                           results_eval=results_eval, results_model=results_model,
                           plot_script=script, plot_div=div,
                           mimetype='text/html')


@experiment_blueprint.route('/predict/<string:experiment_id>', methods=['GET', 'POST'])
@user_decorators.requires_login
def predict(experiment_id):
    experiment = get_experiment_by_id(experiment_id)
    script = None
    div = None

    if request.method == 'POST':
        try:
            task = predict_exp.delay(experiment_id, request.form['raw_text'])
            task.wait()

            if task.status == 'SUCCESS':
                script = task.result[0]
                div = task.result[1]

            return render_template('experiments/prediction.html',
                           experiment=experiment, request = request.form,
                           plot_script=script, plot_div=div,
                           mimetype='text/html')

        except Exception as e:
            flash("Something went wrong: " + str(e.message), 'error')
            return render_template('experiments/prediction.html', experiment=experiment, request = request.form)

    return render_template('experiments/prediction.html', experiment=experiment)

@experiment_blueprint.route('/features_visualisation/<string:experiment_id>')
@user_decorators.requires_login
def visualise_features(experiment_id):
    experiment = get_experiment_by_id(experiment_id)
    if experiment.type == "SVC":
        f_weights = experiment.get_features_weights()
        ds = DataSource.get_by_id(experiment.data_source_id)
        if 'tf-idf' in ds.pre_processing_config.values():
            vectorizer = DATABASE.load_object(ds.vectorizer_handler)
            p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights,
                                                                            vectorizer=vectorizer)
        else:
            p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights,
                                                                            experiment=experiment)
    elif experiment.type == "RF":
        f_weights_df = experiment.get_features_weights()
        p, script, div = ResultVisualiser.visualize_df_feature_importance(f_weights_df, experiment.display_title)
    elif experiment.type == "XGB":
        f_weights_df = experiment.get_features_weights()
        p, script, div = ResultVisualiser.visualize_df_feature_importance(f_weights_df, experiment.display_title)

    if script is not None:
        return render_template('experiments/features.html',
                               experiment=experiment,
                               plot_script=script, plot_div=div,
                               mimetype='text/html')

    return render_template('experiments/features.html', experiment=experiment)


@experiment_blueprint.route('/prediction_overview',  methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def user_experiments_overview_for_prediction():
    # call overview method with the finished experiments that belong to the user
    script = None
    div = None

    if request.method == 'POST':
        try:
            task = predict_overview.delay(session['email'], request.form['raw_text'])
            task.wait()

            if task.status == 'SUCCESS':
                script = task.result[0]
                div = task.result[1]

            return render_template('experiments/prediction_overview.html',
                           request = request.form,
                           plot_script=script, plot_div=div,
                           mimetype='text/html')
        except Exception as e:
            raise
        #     print e.message
        #     return render_template('experiments/prediction_overview.html', request=request.form)

    return render_template('experiments/prediction_overview.html')


@experiment_blueprint.route('/overview',  methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def user_experiments_overview():

    processed_data_source_list = DataSource.get_processed_datasets()
    used_data_source_ids_by_user = Experiment.get_used_data_sources_for_user(user_email=session['email'])
    experiment_ds_dict = {}
    text_explanation_experiments = []

    for ds_id in used_data_source_ids_by_user:
        exp_list = Experiment.get_finished_user_experiments_using_data_id(user_email=session['email'], ds_id=ds_id)
        if 'tf-idf' in DataSource.get_by_id(id=ds_id).pre_processing_config.values():
            for exp in exp_list:
                text_explanation_experiments.append(exp.display_title)
        experiment_ds_dict[ds_id] = exp_list

    if request.method == 'POST':
        finished_experiments = []
        for exp_id in request.form.getlist('compared_experiments'):
            finished_experiments.append(get_experiment_by_id(id=str(exp_id)))

        comparator = ExperimentComparator(finished_experiments)

        script, div = comparator.performComparison()
        script_cm, div_cm = comparator.combineHeatMapPlotsForAllExperiments()
        script.append(script_cm)
        div.append(div_cm)

        return render_template('experiments/overview.html', plot_scripts=script, plot_divs=div,
                       data_sources_db=processed_data_source_list,
                       experiment_ds_dict = experiment_ds_dict,
                       mimetype='text/html')

    return render_template('experiments/overview.html', data_sources_db=processed_data_source_list, experiment_ds_dict = experiment_ds_dict)


@experiment_blueprint.route('/public_prediction_overview', methods=['GET', 'POST'])
@back.anchor
def public_experiments_overview_for_prediction():
    # call overview method with the finished public experiments
    script = None
    div = None

    if request.method == 'POST':
        try:
            task = predict_overview_public.delay(request.form['raw_text'])
            task.wait()

            if task.status == 'SUCCESS':
                script = task.result[0]
                div = task.result[1]

            return render_template('experiments/public_prediction_overview.html',
                                   request=request.form,
                                   plot_script=script, plot_div=div,
                                   mimetype='text/html')
        except Exception as e:
            print e.message
            return render_template('experiments/public_prediction_overview.html', request=request.form)

    return render_template('experiments/public_prediction_overview.html')


@experiment_blueprint.route('/public_overview', methods=['GET', 'POST'])
@back.anchor
def public_experiments_overview():
    processed_data_source_list = DataSource.get_processed_datasets()
    experiment_ds_dict = {}
    text_explanation_experiments = []
    used_data_source_ids = Experiment.get_used_data_sources_for_public()

    for ds_id in used_data_source_ids:
        exp_list = Experiment.get_public_experiments_using_data_id(ds_id=ds_id)
        if 'tf-idf' in DataSource.get_by_id(id=ds_id).pre_processing_config.values():
            for exp in exp_list:
                text_explanation_experiments.append(exp.display_title)
        experiment_ds_dict[ds_id] = exp_list

    if request.method == 'POST':
        finished_experiments = []
        for exp_id in request.form.getlist('compared_experiments'):
            finished_experiments.append(get_experiment_by_id(str(exp_id)))

        comparator = ExperimentComparator(finished_experiments)

        script, div = comparator.performComparison()
        script_cm, div_cm = comparator.combineHeatMapPlotsForAllExperiments()
        script.append(script_cm)
        div.append(div_cm)

        return render_template('experiments/public_overview.html', plot_scripts=script, plot_divs=div,
                               data_sources_db=processed_data_source_list,
                               experiment_ds_dict=experiment_ds_dict,
                               mimetype='text/html')

    return render_template('experiments/public_overview.html', data_sources_db=processed_data_source_list, experiment_ds_dict = experiment_ds_dict)

@experiment_blueprint.route('/hypotheses_testing', methods=['GET', 'POST'])
@user_decorators.requires_login
def hypotheses_testing():
    test_data_sources = DataSource.get_testing_by_user_email(user_email=session['email'])
    # test_data_sources = DataSource.get_by_user_email(user_email=session['email'])
    finished_experiments = Experiment.get_finished_user_experiments(user_email=session['email'])

    if request.method == 'POST':
        experiment = get_experiment_by_id(request.form['hypotheses_experiment'])
        exp_data_source = DataSource.get_by_id(experiment.data_source_id)
        hypotheses_data_source = DataSource.get_by_id(request.form['hypotheses_data_source'])

        df = experiment.populate_hypothesis_df(exp_data_source, hypotheses_data_source)

        try:
            script, div = ExperimentComparator.visualize_hypotheses_using_DF(df, hypotheses_data_source.display_title, experiment.display_title)

            return render_template('experiments/hypotheses.html',  experiments=finished_experiments, test_data_sources=test_data_sources,
                           request = request.form,
                           plot_script=script, plot_div=div,
                           mimetype='text/html')
        except Exception as e:
            flash("Something went wrong: " + str(e.message), 'error')
            return render_template('experiments/hypotheses.html',  experiments=finished_experiments, test_data_sources=test_data_sources)

    return render_template('experiments/hypotheses.html', experiments=finished_experiments, test_data_sources=test_data_sources)


@experiment_blueprint.route('/delete/<string:experiment_id>')
@user_decorators.requires_login
def delete_experiment(experiment_id):
    task = del_exp.delay(experiment_id)
    time.sleep(0.5)
    return back.redirect()

@experiment_blueprint.route('/delete_all')
@user_decorators.requires_login
def delete_all():
    experiments = Experiment.get_by_user_email(session['email'])
    for exp in experiments:
        task = del_exp.delay(exp._id)

    time.sleep(0.5)
    return back.redirect()


