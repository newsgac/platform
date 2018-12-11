from newsgac.learners import LearnerSVC
from newsgac.nlp_tools import TFIDF
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.run import run_pipeline


def test_run_tfidf_svc_pipeline(test_user, data_source_balanced_10):
    pipeline = Pipeline(
        display_title='TFIDF SVC Balanced 10 test',
        user=test_user,
        data_source=data_source_balanced_10,
        nlp_tool=TFIDF.create(),
        learner=LearnerSVC.create()
    )
    pipeline.save()
    run_pipeline(pipeline)
    sk_pipeline = pipeline.sk_pipeline.get()
    result = sk_pipeline.predict(['Dit is een willekeurige tekst'])
    assert sk_pipeline is not None
