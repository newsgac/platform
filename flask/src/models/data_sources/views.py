from __future__ import absolute_import

import time
from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.utils import redirect
from src.app import app
from src.celery_tasks.tasks import process_data, del_data, grid_ds
from src.models.data_sources.data_source import DataSource
import src.models.data_sources.errors as DataSourceErrors
from src.common.back import back
import src.models.users.decorators as user_decorators
from werkzeug.utils import secure_filename
import src.data_engineering.utils as DataUtils
from src.data_engineering.postprocessing import Explanation
from src.models.experiments.experiment import Experiment
from src.run import DATABASE

__author__ = 'abilgin'

data_source_blueprint = Blueprint('data_sources', __name__)

@data_source_blueprint.route('/user')
@user_decorators.requires_login
@back.anchor
def user_data_sources():
    return render_template("data_sources/data_sources.html", data_sources = DataSource.get_by_user_email(session['email']))

@data_source_blueprint.route('/new', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_data_source():
    if request.method == 'POST':
        f = request.files['file']
        if f and DataSource.is_allowed(f.filename):
            filename = secure_filename(f.filename)
            try:
                if DataSource.is_source_unique(user_email= session['email'], display_title=request.form['display_title'].strip()):
                        # file_handler = DATABASE.getGridFS().put(pickle.dumps(f))
                        file_handler = DATABASE.getGridFS().put(f)
                        check = True if 'purpose' in request.form else False
                        new_ds = DataSource(user_email= session['email'], display_title=request.form['display_title'].strip(),
                                            description=request.form['description'], training_purpose=check,
                                            secure_filename=filename, **dict(new_handler=file_handler))
                        new_ds.save_to_db()
                        flash('The file has been successfully uploaded.', 'success')
                        return redirect(url_for("data_sources.user_data_sources"))

            except DataSourceErrors.ResourceError as e:
                flash(e.message, 'error')
                return render_template('data_sources/new_data_source.html', form=request.form)
        else:
            flash('The file type is not supported! Try again using the allowed file formats.', 'error')

    return render_template('data_sources/new_data_source.html')

@data_source_blueprint.route('/<string:data_source_id>')
@user_decorators.requires_login
def get_data_source_page(data_source_id):
    # return the data source page with the type code
    ds = DataSource.get_by_id(data_source_id)

    return render_template('data_sources/data_source.html', data_source=ds)

@data_source_blueprint.route('/article/<string:article_id>')
@user_decorators.requires_login
def get_article_page(article_id):
    # display the processed data source instance which is an article
    art = DataSource.get_processed_article_by_id(article_id)

    return render_template('data_sources/article.html', article=art, descriptions=DataUtils.feature_descriptions)

@data_source_blueprint.route('/article/show/<string:article_id>', methods=['GET'])
@user_decorators.requires_login
def show_article_summary(article_id):
    # display the processed data source instance which is an article
    art = DataSource.get_processed_article_by_id(article_id)

    return render_template('data_sources/article_summary.html', article_summary=art)

@data_source_blueprint.route('/explain/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>', methods=['GET'])
@user_decorators.requires_login
def explain_article_for_experiment(article_id, article_num, genre, experiment_id):
    # art = DataSource.get_processed_article_by_raw_text(article_text)
    art = DataSource.get_processed_article_by_id(article_id)
    exp = Experiment.get_by_id(experiment_id)

    # LIME explanations
    e = Explanation(experiment=exp, article=art, predicted_genre=genre)
    res = e.explain_using_text()

    return render_template('data_sources/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)

@data_source_blueprint.route('/explain_features/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>/', methods=['GET'])
@user_decorators.requires_login
def explain_features_for_experiment(article_id, article_num, genre, experiment_id):
    # art = DataSource.get_processed_article_by_raw_text(article_text)
    art = DataSource.get_processed_article_by_id(article_id)
    exp = Experiment.get_by_id(experiment_id)

    # LIME explanations
    e = Explanation(experiment=exp, article=art, predicted_genre=genre)
    res = e.explain_using_features()

    return render_template('data_sources/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)


@data_source_blueprint.route('/process_real/<string:data_source_id>', methods=['GET'])
@user_decorators.requires_login
def process_data_source_unlabelled(data_source_id):
    data_source = DataSource.get_by_id(data_source_id)
    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = process_data.delay(data_source_id, None)
    else:
        # without celery
        data_source.process_data_source(config=None)

    time.sleep(0.5)
    return redirect(url_for('.get_data_source_page', data_source_id=data_source_id))

@data_source_blueprint.route('/process/<string:data_source_id>', methods=['GET', 'POST'])
@user_decorators.requires_login
def process_data_source(data_source_id):

    data_source = DataSource.get_by_id(data_source_id)
    if request.method == 'POST':
        if data_source.pre_processing_config and not data_source.processing_started:
            if app.DOCKER_RUN:
                # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
                task = process_data.delay(data_source_id, data_source.pre_processing_config)
            else:
                # without celery
                data_source.process_data_source(config=data_source.pre_processing_config)
            time.sleep(0.5)
            return redirect(url_for('.get_data_source_page', data_source_id=data_source_id))

        try:
            config_dict = {}
            if 'auto_data' in request.form:
                config_dict['auto_data'] = True
            else:
                for config, value in request.form.items():
                    if value == "":
                        config_dict[config] = True
                    else:
                        config_dict[config] = value

            if data_source.is_preprocessing_config_unique(config_dict):
                if app.DOCKER_RUN:
                    # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
                    task = process_data.delay(data_source_id, config_dict)
                else:
                    # without celery
                    data_source.process_data_source(config=config_dict)

                time.sleep(0.5)
                return redirect(url_for('.get_data_source_page', data_source_id=data_source_id))
        except DataSourceErrors.ProcessingConfigAlreadyExists as e:
            error = e.message
            flash(error, 'error')
            return render_template('data_sources/configure_data_source.html', request=request.form)

    return render_template('data_sources/configure_data_source.html')


@data_source_blueprint.route('/visualise/<string:data_source_id>')
@user_decorators.requires_login
def visualise_stats(data_source_id):
    ds = DataSource.get_by_id(data_source_id)
    # results = ds.get_stats()
    # plot, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results, title="")
    #
    # return render_template('experiments/results.html',
    #                        experiment=experiment,
    #                        results=results,
    #                        plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),
    #                        mimetype='text/html')

    return render_template('underconstruction.html')

@data_source_blueprint.route('/recommend/<string:data_source_id>')
@user_decorators.requires_login
def apply_grid_search(data_source_id):
    ds = DataSource.get_by_id(data_source_id)

    if app.DOCKER_RUN:
        task = grid_ds.delay(data_source_id)
        task.wait()

        if len(task.result) > 1:
            report_per_score = task.result[0][0]
            feature_reduction = task.result[0][1]
    else:
        report_per_score, feature_reduction = ds.apply_grid_search()

    return render_template('data_sources/recommendation.html', data_source = ds, report_per_score = report_per_score,
                           feature_reduction=feature_reduction)

@data_source_blueprint.route('/overview',  methods=['GET'])
@user_decorators.requires_login
@back.anchor
def sources_overview():
    return render_template('underconstruction.html')

@data_source_blueprint.route('/delete/<string:data_source_id>')
@user_decorators.requires_login
def delete_data_source(data_source_id):

    existing_experiments = Experiment.get_any_user_experiments_using_data_id(user_email=session['email'], ds_id=data_source_id)
    ds = DataSource.get_by_id(data_source_id)
    if len(existing_experiments) > 0:
        error = "There are existing experiments using this data source ("+ str(ds.display_title)+ "). Please delete the experiments connected with this data source first!"
        flash(error, 'error')
        return redirect((url_for('experiments.user_experiments')))

    if app.DOCKER_RUN:
        # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
        task = del_data.delay(data_source_id)
    else:
        # without celery
        DataSource.get_by_id(data_source_id).delete()

    time.sleep(0.5)
    return back.redirect()

@data_source_blueprint.route('/delete_all')
@user_decorators.requires_login
def delete_all():
    existing_experiments = Experiment.get_by_user_email(session['email'])
    if len(existing_experiments) > 0:
        error = "There are existing experiments using the data sources. Please delete all the experiments first!"
        flash(error, 'error')
        return redirect((url_for('experiments.user_experiments')))
    data_sources = DataSource.get_by_user_email(user_email=session['email'])

    for ds in data_sources:
        if app.DOCKER_RUN:
            # with celery (run on bash : celery -A src.celery_tasks.celery_app worker -l info )
            task = del_data.delay(ds._id)
        else:
            # without celery
            DataSource.get_by_id(ds._id).delete()

    time.sleep(0.5)
    return back.redirect()