from __future__ import absolute_import
from bson import ObjectId
from bokeh.embed import components
from bokeh.layouts import gridplot
from flask import Blueprint, render_template, request, session, json, url_for, Response
from pymodm.errors import ValidationError

from newsgac.common.back import back
from newsgac.common.json_encoder import _dumps
from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.tasks import run_pipeline_task
from newsgac.data_sources.models import DataSource
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User
from newsgac.learners.factory import learners, create_learner
from newsgac.nlp_tools import nlp_tools
from newsgac.nlp_tools.factory import create_nlp_tool
from newsgac.visualisation.resultvisualiser import ResultVisualiser

pipeline_blueprint = Blueprint('pipelines', __name__)


learners_dict = {
    learner.tag: {
        'name': learner.name,
        'parameters': learner.parameter_dict(),
        'default':  model_to_dict(learner.create())
    }
    for learner in learners
}


nlp_tools_dict = {
    tool.tag: {
        'name': tool.name,
        'parameters': tool.parameter_dict(),
    }
    for tool in nlp_tools
}

def get_data_sources_dict():
    return {
        str(data_source.pk): {
            'display_title': data_source.display_title,
        }
        for data_source in list(DataSource.objects.all())
    }


@pipeline_blueprint.route('/')
@requires_login
@back.anchor
def user_pipelines():

    pipelines = [
        {
            'id': str(pipeline._id),
            'created': pipeline.created,
            'display_title': pipeline.display_title,
            'nlp_tool': {
                'name': pipeline.nlp_tool.__class__.name,
            },
            'learner': {
                'name': pipeline.learner.__class__.name,
            },
            'data_source': {
                'display_title': pipeline.data_source.display_title
            },
            'task': json.dumps(pipeline.task.as_dict()),
            'json': model_to_json(pipeline, indent=4)

        } for pipeline in list(Pipeline.objects.all())
    ]

    return render_template(
        "pipelines/pipelines.html",
        pipelines=pipelines,
        nlp_tools=nlp_tools_dict,
        learners=learners_dict
    )


@pipeline_blueprint.route('/new/', methods=['GET'])
@pipeline_blueprint.route('/new/<from_pipeline_id>', methods=['GET'])
@requires_login
@back.anchor
def new_pipeline(from_pipeline_id=None):
    if from_pipeline_id is not None:
        pipeline = Pipeline.objects.get({'_id': ObjectId(from_pipeline_id)})
        pipeline.display_title = pipeline.display_title + ' (copy)'
        pipeline._id = None
        pipeline.user = None
    else:
        pipeline = Pipeline.create()

    pipeline = model_to_dict(pipeline)

    pipeline.pop('_id', None)
    pipeline.pop('user', None)
    pipeline.pop('created', None)
    pipeline.pop('updated', None)
    pipeline.pop('task', None)

    return render_template(
        "pipelines/pipeline.html",
        pipeline=_dumps(pipeline),
        data_sources=json.dumps(get_data_sources_dict()),
        nlp_tools=json.dumps(nlp_tools_dict),
        save_url=url_for('pipelines.new_pipeline_save'),
        pipelines_url=url_for('pipelines.user_pipelines'),
        learners=json.dumps(learners_dict)
    )


@pipeline_blueprint.route('/new', methods=['POST'])
@requires_login
def new_pipeline_save():
    pipeline = Pipeline(
        user=User(email=session['email']),
        **request.json
    )

    pipeline.nlp_tool = create_nlp_tool(request.json['nlp_tool']['_tag'], False, **request.json['nlp_tool'])
    pipeline.learner = create_learner(request.json['learner']['_tag'], False, **request.json['learner'])

    try:
        pipeline.save()
        task = run_pipeline_task.delay(str(pipeline._id))
        pipeline.task_id = task.task_id
        pipeline.save()
        return Response(
            model_to_json(pipeline),
            status=201,
            headers={
                'content-type': 'application/json'
            }
        )

    except ValidationError as e:
        return Response(
            json.dumps({'error': e.message}),
            status=400,
            headers={
                'content-type': 'application/json',
            }
        )

    except Exception as e:
        return Response(
            json.dumps({'error': {'serverError': [e.message]}}),
            status=500,
            headers={
                'content-type': 'application/json',
            }
        )


@pipeline_blueprint.route('/<string:pipeline_id>/delete')
@requires_login
def delete_pipeline(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    pipeline.delete()

    return back.redirect()


@pipeline_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for pipeline in list(Pipeline.objects.all()):
        pipeline.delete()

    return back.redirect()


@pipeline_blueprint.route('/<string:pipeline_id>/results')
@requires_login
def visualise_results(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    results_eval = pipeline.result
    results_model = pipeline.result
    p, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_eval, title="Evaluation", ds_param=0.7)
    p_mod, script_mod, div_mod = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_model, title="Model", ds_param=0.7)

    plots = []
    plots.append(p)
    plots.append(p_mod)
    overview_layout = gridplot(plots, ncols=2)
    script, div = components(overview_layout)

    return render_template('pipelines/results.html',
                           pipeline=pipeline,
                           results_eval=results_eval,
                           results_model=results_model,
                           plot_script=script,
                           plot_div=div,
                           mimetype='text/html')



@pipeline_blueprint.route('/<string:pipeline_id>/features')
@requires_login
def visualise_features(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})

    p, script, div = ResultVisualiser.visualize_df_feature_importance(
        pipeline.learner.get_features_weights(),
        pipeline.display_title
    )

    # if type(pipeline.learner) == LearnerSVC:
    #     f_weights = pipeline.learner.get_features_weights()
    #     if 'tf-idf' in type(pipeline.nlp_tool) == TFIDF:
    #         vectorizer = DATABASE.load_object(ds.vectorizer_handler)
    #         p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights,
    #                                                                         vectorizer=vectorizer)
    #     else:
    #         p, script, div = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=f_weights,
    #                                                                         pipeline=pipeline)
    # elif pipeline.type == "RF":
    #     f_weights_df = pipeline.get_features_weights()
    #     p, script, div = ResultVisualiser.visualize_df_feature_importance(f_weights_df, pipeline.display_title)
    # elif pipeline.type == "XGB":
    #     f_weights_df = pipeline.get_features_weights()
    #     p, script, div = ResultVisualiser.visualize_df_feature_importance(f_weights_df, pipeline.display_title)

    if script is not None:
        return render_template('pipelines/features.html',
                               pipeline=pipeline,
                               plot_script=script, plot_div=div,
                               mimetype='text/html')

    return render_template('pipelines/features.html', pipeline=pipeline)


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


