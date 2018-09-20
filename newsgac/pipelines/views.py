from __future__ import absolute_import

from flask import Blueprint, render_template, request, session, flash, json, url_for

from pymodm.errors import ValidationError

from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.data_engineering.data_io import get_feature_names_with_descriptions
from newsgac.data_engineering.utils import features
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User
from newsgac.pipelines.models import NlpTool, nlp_tool_readable, Pipeline
from newsgac.common.back import back

__author__ = 'abilgin'

pipeline_blueprint = Blueprint('pipelines', __name__)


@pipeline_blueprint.route('/')
@requires_login
@back.anchor
def user_pipelines():
    pipelines = list(Pipeline.objects.values())
    return render_template("pipelines/pipelines.html", pipelines=pipelines)


@pipeline_blueprint.route('/new', methods=['GET', 'POST'])
@requires_login
@back.anchor
def new_pipeline():
    if request.method == 'POST':
        pipeline = Pipeline(
            user=User(email=session['email']),
            **request.json
        )
        if pipeline.nlp_tool != NlpTool.FROG:
            pipeline.features = {}

        try:
            pipeline.save()
            flash('The configuration has been saved.', 'success')

        except ValidationError as e:
            flash(str(e), 'error')

    else:
        pipeline = Pipeline.create()

    from newsgac.learners import learners

    learners_dict = {
        learner.tag: {
            'name': learner.name,
            'parameters': learner.parameter_dict(),
            'default':  model_to_dict(learner.create())
        }
        for learner in learners
    }

    return render_template(
        "pipelines/pipeline.html",
        pipeline=model_to_json(pipeline),
        nlp_tools=json.dumps({tool.value: nlp_tool_readable(tool) for tool in NlpTool}),
        features=json.dumps(get_feature_names_with_descriptions()),
        save_url=url_for('pipelines.new_pipeline'),
        learners=json.dumps(learners_dict)
    )


#
# @pipeline_blueprint.route('/new', methods=['GET', 'POST'])
# @user_decorators.requires_login
# @back.anchor
# def create_pipeline():
#     if request.method == 'POST':
#         try:
#             form_dict = request.form.to_dict()
#
#             pipeline = DataSource(**form_dict)
#             pipeline.filename = secure_filename(request.files['file'].filename)
#             pipeline.file = request.files['file']
#             pipeline.user = User(email=session['email'])
#             pipeline.save()
#             flash('The file has been successfully uploaded.', 'success')
#
#             eager_task_result = process.delay(pipeline._id)
#             pipeline.refresh_from_db()
#             pipeline.task = TrackedTask(_id=eager_task_result.id)
#             pipeline.save()
#
#             return redirect(url_for("pipelines.user_pipelines"))
#         except ValidationError as e:
#             if 'filename' in e.message:
#                 flash('The file type is not supported! Try again using the allowed file formats.', 'error')
#
#     return render_template('pipelines/new_pipeline.html', form=request.form)
#
@pipeline_blueprint.route('/<string:pipeline_id>')
@requires_login
def get_pipeline_page(pipeline_id):
    return render_template(
        "pipelines/pipeline.html",
        features=get_feature_names_with_descriptions()
    )
    # return the data source page with the type code
    pass
    # pipeline = DataSource.objects.get({'_id': ObjectId(pipeline_id)})
    # label_count = None
    # try:
    #     label_count = pipeline.count_labels()
    # except Exception:
    #     pass
    #
    # return render_template(
    #     'pipelines/pipeline.html',
    #     pipeline=pipeline,
    #     label_count=label_count
    # )


#
# @pipeline_blueprint.route('/article/<string:article_id>')
# @user_decorators.requires_login
# def get_article_page(article_id):
#     # display the processed data source instance which is an article
#     art = DataSource.get_processed_article_by_id(article_id)
#     ## TODO: bug on adding articles to processed_data
#     return render_template('pipelines/article.html', article=art, descriptions=DataUtils.feature_descriptions)
#
# @pipeline_blueprint.route('/article/show/<string:article_id>', methods=['GET'])
# @user_decorators.requires_login
# def show_article_summary(article_id):
#     # display the processed data source instance which is an article
#     art = DataSource.get_processed_article_by_id(article_id)
#
#     return render_template('pipelines/article_summary.html', article_summary=art)
#
# @pipeline_blueprint.route('/explain/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>', methods=['GET'])
# @user_decorators.requires_login
# def explain_article_for_experiment(article_id, article_num, genre, experiment_id):
#     # art = DataSource.get_processed_article_by_raw_text(article_text)
#     art = DataSource.get_processed_article_by_id(article_id)
#     exp = get_experiment_by_id(experiment_id)
#
#     # LIME explanations
#     e = Explanation(experiment=exp, article=art, predicted_genre=genre)
#     res = e.explain_using_text()
#
#     return render_template('pipelines/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)
#
# @pipeline_blueprint.route('/explain_features/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>/', methods=['GET'])
# @user_decorators.requires_login
# def explain_features_for_experiment(article_id, article_num, genre, experiment_id):
#     # art = DataSource.get_processed_article_by_raw_text(article_text)
#     art = DataSource.get_processed_article_by_id(article_id)
#     exp = get_experiment_by_id(experiment_id)
#
#     # LIME explanations
#     e = Explanation(experiment=exp, article=art, predicted_genre=genre)
#     res = e.explain_using_features()
#
#     return render_template('pipelines/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)
#
#
# @pipeline_blueprint.route('/visualise/<string:pipeline_id>')
# @user_decorators.requires_login
# def visualise_pipeline(pipeline_id):
#     pipeline = DataSource.objects.get({'_id': ObjectId(pipeline_id)})
#
#     script, div = ResultVisualiser.visualize_pipeline_stats(pipeline)
#
#     return render_template('pipelines/pipeline_stats.html',
#                            pipeline=pipeline,
#                            plot_script=script,
#                            plot_div=div,
#                            mimetype='text/html')
#
#
# @pipeline_blueprint.route('/recommend/<string:pipeline_id>')
# @user_decorators.requires_login
# def apply_grid_search(pipeline_id):
#     ds = DataSource.get_by_id(pipeline_id)
#
#     task = grid_ds.delay(pipeline_id)
#     task.wait()
#
#     if len(task.result) > 1:
#         report_per_score = task.result[0][0]
#         feature_reduction = task.result[0][1]
#
#     return render_template('pipelines/recommendation.html', pipeline = ds, report_per_score = report_per_score,
#                            feature_reduction=feature_reduction)
#
# @pipeline_blueprint.route('/overview',  methods=['GET'])
# @user_decorators.requires_login
# @back.anchor
# def sources_overview():
#     return render_template('underconstruction.html')
#
# @pipeline_blueprint.route('/delete/<string:pipeline_id>')
# @user_decorators.requires_login
# def delete_pipeline(pipeline_id):
#
#     existing_experiments = Experiment.get_any_user_experiments_using_data_id(user_email=session['email'], ds_id=pipeline_id)
#     ds = DataSource.get_by_id(pipeline_id)
#     if len(existing_experiments) > 0:
#         error = "There are existing experiments using this data source ("+ str(ds.display_title)+ "). Please delete the experiments connected with this data source first!"
#         flash(error, 'error')
#         return redirect((url_for('experiments.user_experiments')))
#
#     task = del_data.delay(pipeline_id)
#     time.sleep(0.5)
#     return back.redirect()
#

@pipeline_blueprint.route('/delete_all')
@requires_login
def delete_all():
    pass
    # existing_experiments = Experiment.get_by_user_email(session['email'])
    # if len(existing_experiments) > 0:
    #     error = "There are existing experiments using the data sources. Please delete all the experiments first!"
    #     flash(error, 'error')
    #     return redirect((url_for('experiments.user_experiments')))
    # pipelines = DataSource.get_by_user_email(user_email=session['email'])
    #
    # for ds in pipelines:
    #     task = del_data.delay(ds._id)
    #
    # time.sleep(0.5)
    # return back.redirect()
