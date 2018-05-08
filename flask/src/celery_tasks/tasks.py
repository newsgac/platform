from src.celery_tasks.celery_app import celery_app
from src.models.data_sources.data_source import DataSource
from src.models.experiments.experiment import Experiment, ExperimentSVC, ExperimentDT


@celery_app.task(bind=True)
def run_exp(self, exp_id):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='RUNNING', meta={'experiment_id': exp_id})
    if exp.type == "SVC":
        ExperimentSVC.get_by_id(exp_id).run_svc()
    elif exp.type == "DT":
        ExperimentDT.get_by_id(exp_id).run_dt()


@celery_app.task(bind=True)
def del_exp(self, exp_id):
    exp = Experiment.get_by_id(exp_id)
    if exp.type == "SVC":
        ExperimentSVC.get_by_id(exp_id).delete()
    elif exp.type == "DT":
        ExperimentDT.get_by_id(exp_id).delete()

@celery_app.task(bind=True)
def process_data(self, data_source_id, config):
    DataSource.get_by_id(data_source_id).process_data_source(config)
    self.update_state(state='PROCESSING', meta={'data_source_id': data_source_id})

@celery_app.task(bind=True)
def del_data(self, data_source_id):
    DataSource.get_by_id(data_source_id).delete()


@celery_app.task(bind=True, trail=True)
def vis_asp_sem_dist(self, exp_id, keyword, num_neighbours, aspects):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='VISUALISING', meta={'experiment_id':exp_id})
    return exp.visualise_aspect_based_semantic_distance(keyword, num_neighbours, aspects)

@celery_app.task(bind=True, trail=True)
def vis_sem_track(self, exp_id, keyword, num_neighbours, aspects, algorithm, tsne_perp, tsne_iter):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='VISUALISING', meta={'experiment_id':exp_id})
    return exp.visualise_semantic_tracking(keyword, num_neighbours, aspects, algorithm, tsne_perp, tsne_iter)

@celery_app.task(bind=True, trail=True)
def vis_sentiment(self, exp_id, keyword, num_neighbours, lexicon, requested_corpus_list):
    exp = Experiment.get_by_id(exp_id)
    self.update_state(state='VISUALISING', meta={'experiment_id':exp_id})
    return exp.visualise_sentiment_analysis(keyword, num_neighbours,lexicon, requested_corpus_list)