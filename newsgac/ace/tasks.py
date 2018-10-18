from bson import ObjectId

from newsgac.ace.models import ACE
from newsgac.tasks.celery_app import celery_app
from newsgac.visualisation.comparison import PipelineComparator


@celery_app.task(bind=True, trail=True)
def run_ace(self, ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    comparator = PipelineComparator(ace)
    ace.data = comparator.generateAgreementOverview()
    ace.save()
