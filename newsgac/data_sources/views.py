from __future__ import absolute_import

import time
from flask import Blueprint, render_template, request, session, url_for, flash
from pymodm.errors import ValidationError
from werkzeug.utils import redirect

from newsgac.tasks.models import TrackedTask
from newsgac.tasks.tasks import process_data, del_data, grid_ds

import newsgac.data_sources.errors as DataSourceErrors
from newsgac.common.back import back
import newsgac.users.view_decorators as user_decorators
from werkzeug.utils import secure_filename
import newsgac.data_engineering.utils as DataUtils
from newsgac.data_engineering.postprocessing import Explanation
from newsgac.data_sources.models import DataSource
from newsgac.data_sources.tasks import process
from newsgac.models.experiments.experiment import Experiment
from newsgac.models.experiments.factory import get_experiment_by_id
from newsgac.users.models import User
from newsgac.visualisation.resultvisualiser import ResultVisualiser
from newsgac.database import DATABASE
import pandas as pd

__author__ = 'abilgin'

data_source_blueprint = Blueprint('data_sources', __name__)


@data_source_blueprint.route('/')
@user_decorators.requires_login
@back.anchor
def user_data_sources():
    # todo: get users data sources only
    data_sources = list(DataSource.objects.values())
    return render_template("data_sources/data_sources.html", data_sources=data_sources)


@data_source_blueprint.route('/new', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def create_data_source():
    if request.method == 'POST':
        try:
            form_dict = request.form.to_dict()

            data_source = DataSource(**form_dict)
            data_source.filename = secure_filename(request.files['file'].filename)
            data_source.file = request.files['file']
            data_source.user = User(email=session['email'])
            data_source.save()
            flash('The file has been successfully uploaded.', 'success')

            eager_task_result = process.delay(data_source._id)
            data_source.refresh_from_db()
            data_source.task = TrackedTask(_id=eager_task_result.id)
            data_source.save()

            return redirect(url_for("data_sources.user_data_sources"))
        except ValidationError as e:
            if 'filename' in e.message:
                flash('The file type is not supported! Try again using the allowed file formats.', 'error')

    return render_template('data_sources/new_data_source.html', form=request.form)

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
    ## TODO: bug on adding articles to processed_data
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
    exp = get_experiment_by_id(experiment_id)

    # LIME explanations
    e = Explanation(experiment=exp, article=art, predicted_genre=genre)
    res = e.explain_using_text()

    return render_template('data_sources/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)

@data_source_blueprint.route('/explain_features/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>/', methods=['GET'])
@user_decorators.requires_login
def explain_features_for_experiment(article_id, article_num, genre, experiment_id):
    # art = DataSource.get_processed_article_by_raw_text(article_text)
    art = DataSource.get_processed_article_by_id(article_id)
    exp = get_experiment_by_id(experiment_id)

    # LIME explanations
    e = Explanation(experiment=exp, article=art, predicted_genre=genre)
    res = e.explain_using_features()

    return render_template('data_sources/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)


@data_source_blueprint.route('/process_real/<string:data_source_id>', methods=['GET'])
@user_decorators.requires_login
def process_data_source_unlabelled(data_source_id):
    data_source = DataSource.get_by_id(data_source_id)
    task = process_data.delay(data_source_id, None)

    time.sleep(0.5)
    return redirect(url_for('.get_data_source_page', data_source_id=data_source_id))

@data_source_blueprint.route('/process/<string:data_source_id>', methods=['GET', 'POST'])
@user_decorators.requires_login
def process_data_source(data_source_id):

    data_source = DataSource.get_by_id(data_source_id)
    if request.method == 'POST':
        if data_source.pre_processing_config and not data_source.processing_started:
            task = process_data.delay(data_source_id, data_source.pre_processing_config)
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
                task = process_data.delay(data_source_id, config_dict)
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

    print (ds.stats_all)
    stats_df = pd.DataFrame(ds.stats_all, columns=ds.stats_all.keys())
    stats_df.fillna(0, inplace=True)

    script, div = ResultVisualiser.visualize_df_stats(stats_df, ds.display_title)

    return render_template('data_sources/data_source_stats.html',
                           data_source=ds,
                           plot_script=script, plot_div=div,
                           mimetype='text/html')


@data_source_blueprint.route('/recommend/<string:data_source_id>')
@user_decorators.requires_login
def apply_grid_search(data_source_id):
    ds = DataSource.get_by_id(data_source_id)

    task = grid_ds.delay(data_source_id)
    task.wait()

    if len(task.result) > 1:
        report_per_score = task.result[0][0]
        feature_reduction = task.result[0][1]

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

    task = del_data.delay(data_source_id)
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
        task = del_data.delay(ds._id)

    time.sleep(0.5)
    return back.redirect()