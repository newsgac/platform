
from bson import ObjectId
from bokeh.embed import components
from flask import Blueprint, render_template, request, session, json, url_for, Response
from pymodm.errors import ValidationError
from sklearn.pipeline import FeatureUnion, Pipeline as SKPipeline

from newsgac.common.back import back
from newsgac.common.json_encoder import _dumps
from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.learners import GridSearch
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.tasks import run_pipeline_task, run_grid_search_task
from newsgac.data_sources.models import DataSource
from newsgac.stop_words.models import StopWords
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User
from newsgac.learners.factory import learners, create_learner
from newsgac.nlp_tools import nlp_tools
from newsgac.nlp_tools.factory import create_nlp_tool
from newsgac.pipelines.plots import confusion_matrix_plot, feature_weights

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
        # for data_source in list(DataSource.objects.raw({'training_purpose': True}))
    }


def get_stop_words_dict_list():
    return [{
        'display_title': stop_words.display_title,
        'description': stop_words.description,
        'filename': stop_words.filename,
        'id': str(stop_words._id)
    } for stop_words in StopWords.objects.all()]



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
        stop_words=json.dumps(get_stop_words_dict_list()),
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
        pipeline.refresh_from_db()
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
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})
    results_eval = pipeline.result
    results_model = pipeline.result

    p = confusion_matrix_plot(pipeline=pipeline, ds_param=0.66)
    script, div = components(p)

    p_features = feature_weights(pipeline=pipeline)
    if p_features:
        f_script, f_div = components(p_features)
    else:
        f_script, f_div = (None, None)

    return render_template(
        'pipelines/results.html',
        pipeline=pipeline,
        results_eval=results_eval,
        results_model=results_model,
        plot_script=script,
        plot_div=div,
        plot_feature_script=f_script,
        plot_feature_div=f_div,
        mimetype='text/html',
        mermaid=get_mermaid(pipeline.get_sk_pipeline())
    )
