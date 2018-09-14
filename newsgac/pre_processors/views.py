from __future__ import absolute_import
from flask import Blueprint, render_template, request, session, flash, json, url_for

from pymodm.errors import ValidationError

from newsgac.common.utils import model_to_json
from newsgac.data_engineering.data_io import get_feature_names_with_descriptions
from newsgac.data_engineering.utils import features
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User
from newsgac.pre_processors.models import PreProcessor, NlpTool, nlp_tool_readable
from newsgac.common.back import back

__author__ = 'abilgin'

pre_processor_blueprint = Blueprint('pre_processors', __name__)


@pre_processor_blueprint.route('/')
@requires_login
@back.anchor
def user_pre_processors():
    pre_processors = list(PreProcessor.objects.values())
    return render_template("pre_processors/pre_processors.html", pre_processors=pre_processors)


@pre_processor_blueprint.route('/new', methods=['GET', 'POST'])
@requires_login
@back.anchor
def new_pre_processor():
    if request.method == 'POST':
        pre_processor = PreProcessor(
            user=User(email=session['email']),
            **request.json
        )
        if pre_processor.nlp_tool != NlpTool.FROG:
            pre_processor.features = {}

        try:
            pre_processor.save()
            flash('The configuration has been saved.', 'success')

        except ValidationError as e:
                flash(str(e), 'error')

    else:
        pre_processor = PreProcessor.create()

    return render_template(
        "pre_processors/pre_processor.html",
        pre_processor=model_to_json(pre_processor),
        nlp_tools=json.dumps({tool.value: nlp_tool_readable(tool) for tool in NlpTool}),
        features=json.dumps(get_feature_names_with_descriptions()),
        save_url=url_for('pre_processors.new_pre_processor')
    )

#
# @pre_processor_blueprint.route('/new', methods=['GET', 'POST'])
# @user_decorators.requires_login
# @back.anchor
# def create_pre_processor():
#     if request.method == 'POST':
#         try:
#             form_dict = request.form.to_dict()
#
#             pre_processor = DataSource(**form_dict)
#             pre_processor.filename = secure_filename(request.files['file'].filename)
#             pre_processor.file = request.files['file']
#             pre_processor.user = User(email=session['email'])
#             pre_processor.save()
#             flash('The file has been successfully uploaded.', 'success')
#
#             eager_task_result = process.delay(pre_processor._id)
#             pre_processor.refresh_from_db()
#             pre_processor.task = TrackedTask(_id=eager_task_result.id)
#             pre_processor.save()
#
#             return redirect(url_for("pre_processors.user_pre_processors"))
#         except ValidationError as e:
#             if 'filename' in e.message:
#                 flash('The file type is not supported! Try again using the allowed file formats.', 'error')
#
#     return render_template('pre_processors/new_pre_processor.html', form=request.form)
#
@pre_processor_blueprint.route('/<string:pre_processor_id>')
@requires_login
def get_pre_processor_page(pre_processor_id):
    return render_template(
        "pre_processors/pre_processor.html",
        features=get_feature_names_with_descriptions()
    )
    # return the data source page with the type code
    pass
    # pre_processor = DataSource.objects.get({'_id': ObjectId(pre_processor_id)})
    # label_count = None
    # try:
    #     label_count = pre_processor.count_labels()
    # except Exception:
    #     pass
    #
    # return render_template(
    #     'pre_processors/pre_processor.html',
    #     pre_processor=pre_processor,
    #     label_count=label_count
    # )
#
# @pre_processor_blueprint.route('/article/<string:article_id>')
# @user_decorators.requires_login
# def get_article_page(article_id):
#     # display the processed data source instance which is an article
#     art = DataSource.get_processed_article_by_id(article_id)
#     ## TODO: bug on adding articles to processed_data
#     return render_template('pre_processors/article.html', article=art, descriptions=DataUtils.feature_descriptions)
#
# @pre_processor_blueprint.route('/article/show/<string:article_id>', methods=['GET'])
# @user_decorators.requires_login
# def show_article_summary(article_id):
#     # display the processed data source instance which is an article
#     art = DataSource.get_processed_article_by_id(article_id)
#
#     return render_template('pre_processors/article_summary.html', article_summary=art)
#
# @pre_processor_blueprint.route('/explain/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>', methods=['GET'])
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
#     return render_template('pre_processors/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)
#
# @pre_processor_blueprint.route('/explain_features/<string:article_id>/<string:article_num>/<string:genre>/<string:experiment_id>/', methods=['GET'])
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
#     return render_template('pre_processors/explanation.html', experiment=exp, article=art, article_num=article_num, exp=res)
#
#
# @pre_processor_blueprint.route('/visualise/<string:pre_processor_id>')
# @user_decorators.requires_login
# def visualise_pre_processor(pre_processor_id):
#     pre_processor = DataSource.objects.get({'_id': ObjectId(pre_processor_id)})
#
#     script, div = ResultVisualiser.visualize_pre_processor_stats(pre_processor)
#
#     return render_template('pre_processors/pre_processor_stats.html',
#                            pre_processor=pre_processor,
#                            plot_script=script,
#                            plot_div=div,
#                            mimetype='text/html')
#
#
# @pre_processor_blueprint.route('/recommend/<string:pre_processor_id>')
# @user_decorators.requires_login
# def apply_grid_search(pre_processor_id):
#     ds = DataSource.get_by_id(pre_processor_id)
#
#     task = grid_ds.delay(pre_processor_id)
#     task.wait()
#
#     if len(task.result) > 1:
#         report_per_score = task.result[0][0]
#         feature_reduction = task.result[0][1]
#
#     return render_template('pre_processors/recommendation.html', pre_processor = ds, report_per_score = report_per_score,
#                            feature_reduction=feature_reduction)
#
# @pre_processor_blueprint.route('/overview',  methods=['GET'])
# @user_decorators.requires_login
# @back.anchor
# def sources_overview():
#     return render_template('underconstruction.html')
#
# @pre_processor_blueprint.route('/delete/<string:pre_processor_id>')
# @user_decorators.requires_login
# def delete_pre_processor(pre_processor_id):
#
#     existing_experiments = Experiment.get_any_user_experiments_using_data_id(user_email=session['email'], ds_id=pre_processor_id)
#     ds = DataSource.get_by_id(pre_processor_id)
#     if len(existing_experiments) > 0:
#         error = "There are existing experiments using this data source ("+ str(ds.display_title)+ "). Please delete the experiments connected with this data source first!"
#         flash(error, 'error')
#         return redirect((url_for('experiments.user_experiments')))
#
#     task = del_data.delay(pre_processor_id)
#     time.sleep(0.5)
#     return back.redirect()
#

@pre_processor_blueprint.route('/delete_all')
@requires_login
def delete_all():
    pass
    # existing_experiments = Experiment.get_by_user_email(session['email'])
    # if len(existing_experiments) > 0:
    #     error = "There are existing experiments using the data sources. Please delete all the experiments first!"
    #     flash(error, 'error')
    #     return redirect((url_for('experiments.user_experiments')))
    # pre_processors = DataSource.get_by_user_email(user_email=session['email'])
    #
    # for ds in pre_processors:
    #     task = del_data.delay(ds._id)
    #
    # time.sleep(0.5)
    # return back.redirect()