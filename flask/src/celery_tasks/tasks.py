from __future__ import absolute_import
from src.celery_tasks.celery_app import celery_app
from src.models.data_sources.data_source import DataSource
from src.models.experiments.experiment import Experiment, ExperimentSVC, ExperimentRF, ExperimentNB
from src.visualisation.comparison import ExperimentComparator


@celery_app.task(bind=True)
def run_exp(self, exp_id):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='RUNNING', meta={'experiment_id': exp_id})
    if exp.type == "SVC":
        ExperimentSVC.get_by_id(exp_id).run_svc()
    elif exp.type == "RF":
        ExperimentRF.get_by_id(exp_id).run_rf()
    elif exp.type == "NB":
        ExperimentNB.get_by_id(exp_id).run_nb()


@celery_app.task(bind=True)
def del_exp(self, exp_id):
    exp = Experiment.get_by_id(exp_id)
    if exp.type == "SVC":
        ExperimentSVC.get_by_id(exp_id).delete()
    elif exp.type == "RF":
        ExperimentRF.get_by_id(exp_id).delete()
    elif exp.type == "NB":
        ExperimentNB.get_by_id(exp_id).delete()

@celery_app.task(bind=True)
def process_data(self, data_source_id, config):
    DataSource.get_by_id(data_source_id).process_data_source(config)
    self.update_state(state='PROCESSING', meta={'data_source_id': data_source_id})

@celery_app.task(bind=True)
def del_data(self, data_source_id):
    DataSource.get_by_id(data_source_id).delete()

@celery_app.task(bind=True, trail=True)
def grid_ds(self, data_source_id):
    self.update_state(state='OPTIMIZING')
    return DataSource.get_by_id(data_source_id).apply_grid_search()

@celery_app.task(bind=True, trail=True)
def predict_exp(self, exp_id, raw_text, data_source):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='PREDICTING', meta={'experiment_id':exp_id})
    return exp.predict(raw_text, data_source)

@celery_app.task(bind=True, trail=True)
def predict_overview(self, user_email, raw_text):
    finished_experiments = Experiment.get_finished_user_experiments(user_email)
    comparator = ExperimentComparator(finished_experiments)
    self.update_state(state='PREDICTING')
    return comparator.visualise_prediction_comparison(raw_text)

@celery_app.task(bind=True, trail=True)
def predict_overview_public(self, raw_text):
    finished_experiments = Experiment.get_public_experiments()
    comparator = ExperimentComparator(finished_experiments)
    self.update_state(state='PREDICTING')
    return comparator.visualise_prediction_comparison(raw_text)

@celery_app.task(bind=True, trail=True)
def ace_exp(self, finished_exp_ids):
    processed_data_source_list = DataSource.get_processed_datasets()
    finished_experiments = []
    for exp_id in finished_exp_ids:
        finished_experiments.append(Experiment.get_by_id(id=str(exp_id)))
    comparator = ExperimentComparator(finished_experiments)
    # get the test articles
    test_articles_genres = comparator.retrieveUniqueTestArticleGenreTuplesBasedOnRawText(
        processed_data_source_list)
    self.update_state(state='ANALYSING')
    return comparator.generateAgreementOverview(test_articles_genres)

@celery_app.task(bind=True)
def hyp_exp(self, experiment_id, hypotheses_data_source_id):
    experiment = Experiment.get_by_id(experiment_id)
    exp_data_source = DataSource.get_by_id(experiment.data_source_id)
    hypotheses_data_source = DataSource.get_by_id(hypotheses_data_source_id)
    self.update_state(state='TESTING')
    return experiment.populate_hypothesis_df(exp_data_source, hypotheses_data_source)


