import numpy
from bson import ObjectId
from newsgac.ace.models import ACE
from newsgac.tasks.celery_app import celery_app
from newsgac.tasks.progress import report_progress


def get_predictions(articles, pipelines):
    # todo: parallelize
    # pipeline predictions are (hopefully) already parallelized for multiple articles at the same time
    # we could still paralellize multiple pipelines
    predictions = []
    for idx, pipeline in enumerate(pipelines):
        predictions.append(
            pipeline.sk_pipeline.predict([article.raw_text for article in articles]))
        report_progress('ace', (idx + 1) / float(len(pipelines)))
    # transpose so first axis is now article e.g. predictions[0][1] is article 0, pipeline 1
    return numpy.array(predictions).transpose()


@celery_app.task(bind=True, trail=True)
def run_ace(self, ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    ace.predictions = get_predictions(ace.data_source.articles, ace.pipelines)
    ace.save()
