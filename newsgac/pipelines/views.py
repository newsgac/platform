
from bson import ObjectId
from bokeh.embed import components
from bokeh.layouts import gridplot
from flask import Blueprint, render_template, request, session, json, url_for, Response
from lime.lime_tabular import LimeTabularExplainer
from pymodm.errors import ValidationError
from scipy.sparse import csr_matrix
from sklearn.pipeline import FeatureUnion, Pipeline as SKPipeline

from newsgac.common.back import back
from newsgac.common.json_encoder import _dumps
from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.learners import GridSearch
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.tasks import run_pipeline_task, run_grid_search_task
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
        # for data_source in list(DataSource.objects.all())
        for data_source in list(DataSource.objects.raw({'training_purpose': True}))
    }


@pipeline_blueprint.route('/')
@requires_login
@back.anchor
def overview():
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
            'task': pipeline.task

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
def new(from_pipeline_id=None):
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
        save_url=url_for('pipelines.new_save'),
        pipelines_url=url_for('pipelines.overview'),
        learners=json.dumps(learners_dict)
    )


@pipeline_blueprint.route('/new', methods=['POST'])
@requires_login
def new_save():
    pipeline = Pipeline(
        user=User(email=session['email']),
        **request.json
    )

    pipeline.nlp_tool = create_nlp_tool(request.json['nlp_tool']['_tag'], False, **request.json['nlp_tool'])
    pipeline.learner = create_learner(request.json['learner']['_tag'], False, **request.json['learner'])

    try:
        pipeline.result = None
        pipeline.save()
        if isinstance(pipeline.learner, GridSearch):
            task = run_grid_search_task.delay(str(pipeline._id))
        else:
            task = run_pipeline_task.delay(str(pipeline._id))
        pipeline.task.task_id = task.task_id
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
def delete(pipeline_id):
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    pipeline.delete()

    return back.redirect()


@pipeline_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for pipeline in list(Pipeline.objects.all()):
        pipeline.delete()

    return back.redirect()


def get_pipeline_step(step, label='', from_label=None, to_label=None):
    output = ''
    if isinstance(step[1], SKPipeline):
        for i, sub_step in enumerate(step[1].steps):
            output += get_pipeline_step(
                sub_step,
                label + '_' + str(i),
                from_label if i==0 else None,
                to_label if i==len(step[1].steps)-1 else label + '_' + str(i+1)
            )

    elif isinstance(step[1], FeatureUnion):
        if from_label:
            output += '%s --> %s\n' % (from_label, label)
        output += '%s[%s: %s]\n' % (label, step[0], step[1].__class__.__name__)
        for i, sub_step in enumerate(step[1].transformer_list):
            output += get_pipeline_step(
                sub_step,
                label + '_' + str(i),
                label,
                to_label
            )

    else:
        output += '%s[%s: %s]\n' % (label, step[0], step[1].__class__.__name__)
        if from_label:
            output += '%s --> %s\n' % (from_label, label)
        if to_label:
            output += '%s --> %s\n' % (label, to_label)
    return output


def get_mermaid(pipeline):
    output = 'graph TD\n'
    output += 'Source[Data source]\n'
    output += 'Result[End result]\n'
    output += get_pipeline_step(('Root', pipeline), 'Root', from_label='Source', to_label='Result')

    # output += get_mermaid_pipeline(pipeline)
    return output


@pipeline_blueprint.route('/<string:pipeline_id>/results')
@requires_login
def visualise_results(pipeline_id):
    # TODO: refactor
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    sk_pipeline = pipeline.sk_pipeline.get()
    classifier = sk_pipeline.named_steps['Classifier']
    results_eval = pipeline.result
    results_model = pipeline.result
    p, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_eval, title="Evaluation", ds_param=0.7)
    # p_mod, script_mod, div_mod = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results_model, title="Model", ds_param=0.7)
    script_f = ''
    div_f = ''
    # TODO: check for nb
    # TODO: _svc because it's crashing atm
    if pipeline.learner._tag in ['_svc']:
        if classifier.kernel == 'linear':
            coefficients = classifier.coef_
            vectorized_pipeline = sk_pipeline.named_steps['FeatureExtraction'].transformer_list[0][0] == 'TFIDF'
            names = sk_pipeline.named_steps['FeatureExtraction'].get_feature_names()
            # get vectorizer for bow
            if isinstance(coefficients, csr_matrix):
                coefficients = coefficients.toarray()
            p_f, script_f, div_f = ResultVisualiser.retrievePlotForFeatureWeights(coefficients=coefficients, names=names, vectorized_pipeline=vectorized_pipeline )
    elif pipeline.learner.tag in ['xgb']:
        from pandas import DataFrame
        from collections import OrderedDict

        feature_weights = classifier.get_booster().get_fscore()
        sorted_fw = OrderedDict(sorted(list(feature_weights.items()), key=lambda t: t[0]))
        sorted_keys = sorted(sk_pipeline.named_steps['FeatureExtraction'].get_feature_names())
        print(sorted_fw)

        feat_importances = []
        for (ft, score) in list(sorted_fw.items()):
            index = int(ft.split("f")[1])
            feat_importances.append({'Feature': sorted_keys[index], 'Importance': score})
        feat_importances = DataFrame(feat_importances)
        feat_importances = feat_importances.sort_values(
            by='Importance', ascending=True).reset_index(drop=True)
        # Divide the importances by the sum of all importances
        # to get relative importances. By using relative importances
        # the sum of all importances will equal to 1, i.e.,
        # np.sum(feat_importances['importance']) == 1
        feat_importances['Importance'] /= feat_importances['Importance'].sum()
        feat_importances = feat_importances.round(3)

        p_f, script_f, div_f = ResultVisualiser.visualize_df_feature_importance(feat_importances, pipeline.display_title)
    elif pipeline.learner.tag in ['rf']:
        from pandas import DataFrame
        feature_weights = classifier.feature_importances_
        sorted_keys = sorted(sk_pipeline.named_steps['FeatureExtraction'].get_feature_names())

        feat_importances = []
        for (ft, key) in zip(feature_weights, sorted_keys):
            feat_importances.append({'Feature': key, 'Importance': ft})
        feat_importances = DataFrame(feat_importances)
        feat_importances = feat_importances.sort_values(
            by='Importance', ascending=True).reset_index(drop=True)
        # Divide the importances by the sum of all importances
        # to get relative importances. By using relative importances
        # the sum of all importances will equal to 1, i.e.,
        # np.sum(feat_importances['importance']) == 1
        feat_importances['Importance'] /= feat_importances['Importance'].sum()
        feat_importances = feat_importances.round(3)

        p_f, script_f, div_f = ResultVisualiser.visualize_df_feature_importance(feat_importances,
                                                                                pipeline.display_title)

    plots = []
    plots.append(p)
    overview_layout = gridplot(plots, ncols=2)
    script, div = components(overview_layout)

    return render_template('pipelines/results.html',
                           pipeline=pipeline,
                           results_eval=results_eval,
                           results_model=results_model,
                           plot_script=script,
                           plot_div=div,
                           plot_feature_script=script_f,
                           plot_feature_div=div_f,
                           mimetype='text/html',
                           mermaid=get_mermaid(pipeline.get_sk_pipeline())
                           )



