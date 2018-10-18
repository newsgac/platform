import pytest

from newsgac.learners import LearnerNB
from newsgac.nlp_tools import Frog
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.run import run_pipeline


def test_run_frog_nb_pipeline(test_user, data_source_balanced_10):
    pipeline = Pipeline(
        display_title='Frog NB Balanced 10 test',
        user=test_user,
        data_source=data_source_balanced_10,
        nlp_tool=Frog.create(),
        learner=LearnerNB.create()
    )
    pipeline.save()
    run_pipeline(pipeline)
    assert pipeline.sk_pipeline is not None


@pytest.mark.timeout(20)
def test_second_run_uses_cache(test_user, data_source_balanced_10):
    pipeline = Pipeline(
        display_title='Frog NB Balanced 10 test (copy)',
        user=test_user,
        data_source=data_source_balanced_10,
        nlp_tool=Frog.create(),
        learner=LearnerNB.create()
    )
    pipeline.save()
    run_pipeline(pipeline)
    assert pipeline.sk_pipeline is not None
