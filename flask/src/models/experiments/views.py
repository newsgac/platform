from __future__ import absolute_import
from __future__ import division

from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect

from src.app import app
import src.data_engineering.data_io as DataIO
from src.models.configurations.configuration_svc import ConfigurationSVC
from src.common.back import back
from src.run import DATABASE
from src.models.configurations.configuration_rf import ConfigurationRF
from src.models.experiments.experiment import Experiment, ExperimentRF, ExperimentSVC
import src.models.users.decorators as user_decorators
import src.models.configurations.errors as ConfigurationErrors
from src.models.data_sources.data_source import DataSource
from src.celery_tasks.tasks import run_exp, del_exp
import time
import dill
from bokeh.resources import INLINE

from src.visualisation.comparison import ExperimentComparator
from src.visualisation.resultvisualiser import ResultVisualiser

from decimal import *
getcontext().prec = 2

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
        return render_template('experiments/experiment_svc.html', experiment=experiment)
    elif experiment.type == "RF":
        return render_template('experiments/experiment_rf.html', experiment=experiment)
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
        elif exp.type == "RF":
            ExperimentRF.get_by_id(experiment_id).run_rf()

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
    data_source = DataSource.get_by_id(experiment.data_source_id)

    if request.method == 'POST':
        sorted_prediction_results = experiment.predict(request.form['raw_text'], data_source)
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
        ds = DataSource.get_by_id(experiment.data_source_id)
        if 'nltk' in ds.pre_processing_config.values():
            pickled_model = DATABASE.getGridFS().get(ds.vectorizer_handler).read()
            vectorizer = dill.loads(pickled_model)
            p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights, vectorizer=vectorizer)
        else:
            p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights)

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

    processed_data_source_list = DataSource.get_processed_datasets()
    used_data_source_ids_by_user = Experiment.get_used_data_sources_for_user(user_email=session['email'])
    experiment_ds_dict = {}
    text_explanation_experiments = []

    for ds_id in used_data_source_ids_by_user:
        exp_list = Experiment.get_finished_user_experiments_using_data_id(user_email=session['email'], ds_id=ds_id)
        if 'nltk' in DataSource.get_by_id(id=ds_id).pre_processing_config.values():
            for exp in exp_list:
                text_explanation_experiments.append(exp.display_title)
        experiment_ds_dict[ds_id] = exp_list

    if request.method == 'POST':
        finished_experiments = []
        for exp_id in request.form.getlist('compared_experiments'):
            finished_experiments.append(Experiment.get_by_id(id=str(exp_id)))

        comparator = ExperimentComparator(finished_experiments)

        script, div = comparator.performComparison()
        script_cm, div_cm = comparator.combineHeatMapPlotsForAllExperiments()
        script.append(script_cm)
        div.append(div_cm)

        return render_template('experiments/overview.html', plot_scripts=script, plot_divs=div,
                       js_resources=INLINE.render_js(), data_sources_db=processed_data_source_list,
                       experiment_ds_dict = experiment_ds_dict,
                       css_resources=INLINE.render_css(), mimetype='text/html')

    return render_template('experiments/overview.html', data_sources_db=processed_data_source_list, experiment_ds_dict = experiment_ds_dict)

@experiment_blueprint.route('/analyse_compare_explain',  methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def user_experiments_analyse_compare_explain():
    if not session['email']:
        return redirect(url_for("experiments.public_overview"))

    processed_data_source_list = DataSource.get_processed_datasets()
    used_data_source_ids_by_user = Experiment.get_used_data_sources_for_user(user_email=session['email'])
    experiment_ds_dict = {}
    text_explanation_experiments = []

    for ds_id in used_data_source_ids_by_user:
        exp_list = Experiment.get_finished_user_experiments_using_data_id(user_email=session['email'], ds_id=ds_id)
        if 'nltk' in DataSource.get_by_id(id=ds_id).pre_processing_config.values():
            for exp in exp_list:
                text_explanation_experiments.append(exp.display_title)
        experiment_ds_dict[ds_id] = exp_list

    if request.method == 'POST':
        finished_experiments = []
        for exp_id in request.form.getlist('compared_experiments'):
            finished_experiments.append(Experiment.get_by_id(id=str(exp_id)))

        comparator = ExperimentComparator(finished_experiments)

        # get the test articles
        test_articles_genres = comparator.retrieveUniqueTestArticleGenreTuplesBasedOnRawText(processed_data_source_list)
        tabular_data_dict, combinations = comparator.generateAgreementOverview(test_articles_genres)

        return render_template('experiments/analyse_compare_explain.html',
                       js_resources=INLINE.render_js(), data_sources_db=processed_data_source_list,
                       experiment_ds_dict = experiment_ds_dict, text_explanation_experiments=text_explanation_experiments,
                       articles=test_articles_genres, tabular_data_dict=tabular_data_dict,
                       combinations=combinations,
                       css_resources=INLINE.render_css(), mimetype='text/html')

    return render_template('experiments/analyse_compare_explain.html', data_sources_db=processed_data_source_list, experiment_ds_dict = experiment_ds_dict)

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

@experiment_blueprint.route('/hypotheses_testing', methods=['GET', 'POST'])
@user_decorators.requires_login
def hypotheses_testing():
    test_data_sources = DataSource.get_testing_by_user_email(user_email=session['email'])
    finished_experiments = Experiment.get_finished_user_experiments(user_email=session['email'])

    if request.method == 'POST':
        experiment = Experiment.get_by_id(request.form['hypotheses_experiment'])
        exp_data_source = DataSource.get_by_id(experiment.data_source_id)
        hypotheses_data_source = DataSource.get_by_id(request.form['hypotheses_data_source'])

        data = {}
        articles = hypotheses_data_source.get_test_instances()
        import pandas as pd
        for article in articles:
            #year extraction
            date_from_db = article['date'].split("-")[2]
            if date_from_db not in data.keys():
                data[date_from_db] = {}

            prediction = (experiment.predict(article['article_raw_text'], exp_data_source)).keys()[0]
            if prediction not in data[date_from_db].keys():
                data[date_from_db][prediction] = 0
            data[date_from_db][prediction] += 1

        normalised_data = {}
        for date in data:
            normalised_data[date] = {}
            for genre in data[date]:
                normalised_data[date][genre] = (round( data[date][genre] * 100 / len(articles), 2))

        df = pd.DataFrame(normalised_data, columns=data.keys())
        df.fillna(0, inplace=True)
        try:
            script, div = ExperimentComparator.visualize_hypotheses_using_DF(df, hypotheses_data_source.display_title, experiment.display_title)
            print data
            print normalised_data
            return render_template('experiments/hypotheses.html',  experiments=finished_experiments, test_data_sources=test_data_sources,
                           request = request.form,
                           plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
                           mimetype='text/html')
        except Exception as e:
            flash("Something went wrong: " + str(e.message), 'error')
            return render_template('experiments/hypotheses.html',  experiments=finished_experiments, test_data_sources=test_data_sources)

    return render_template('experiments/hypotheses.html', experiments=finished_experiments, test_data_sources=test_data_sources)


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
        elif exp.type == "RF":
            ExperimentRF.get_by_id(experiment_id).delete()

    time.sleep(0.5)
    return back.redirect()


