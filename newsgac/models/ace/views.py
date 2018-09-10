from flask import Blueprint, render_template, request, session

from newsgac.tasks.tasks import run_ace
from newsgac.common.back import back
import newsgac.users.view_decorators as user_decorators
from newsgac.database import DATABASE
from newsgac.models.ace.ace import Ace
from newsgac.models.data_sources.data_source_old import DataSource
from newsgac.models.experiments.experiment import Experiment
from newsgac.models.experiments.factory import get_experiment_by_id

__author__ = 'tom'

ace_blueprint = Blueprint('ace', __name__)


@ace_blueprint.route('/', methods=['GET', 'POST'])
@user_decorators.requires_login
@back.anchor
def ace_view():
    if request.method == 'POST':
        finished_experiments = []
        for exp_id in request.form.getlist('compared_experiments'):
            finished_experiments.append(get_experiment_by_id(str(exp_id)))

        ace = Ace.create(finished_experiments, session['email'])
        ace.save_to_db()
        run_ace.delay(ace._id)

    def transform_ace_run(ace_run):
        def transform_experiment(experiment_id):
            experiment = get_experiment_by_id(experiment_id)
            return dict(
                display_title=experiment.display_title,
                id=experiment._id
            )

        return dict(
            id=ace_run['_id'],
            created=ace_run['created'],
            experiments=map(transform_experiment, ace_run['experiments']),
            is_processing=ace_run['result'] is None,
        )

    last_runs = map(transform_ace_run, Ace.get_all_by_user_email(session['email']))

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

    return render_template('ace/overview.html',
                           data_sources_db=processed_data_source_list,
                           experiment_ds_dict=experiment_ds_dict,
                           last_runs=last_runs
                           )


@ace_blueprint.route('/<string:ace_id>')
@user_decorators.requires_login
def view_ace_run(ace_id):
    ace = Ace.get_by_id(ace_id)
    data = DATABASE.load_object(ace.result)
    return render_template(
        'ace/run.html',
        **data
    )
