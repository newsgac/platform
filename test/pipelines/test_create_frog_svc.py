from sklearn.preprocessing import RobustScaler

from learners import LearnerSVC, LearnerNB
from newsgac.nlp_tools import Frog
from newsgac.pipelines.models import Pipeline
from newsgac.pipelines.run import run_pipeline


def test_create_frog_svc_pipeline(test_user, data_source_balanced_10):
    pipeline = Pipeline(
        display_title='Frog SVC Balanced 10 test',
        user=test_user,
        data_source=data_source_balanced_10,
        nlp_tool=Frog.create(),
        learner=LearnerNB.create()
    )
    pipeline.save()
    run_pipeline(pipeline)
    print(pipeline.features.data)
    assert 1==2


# def test_scaler(frog_features):
#     sorted_features = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
#
#
#     scaled_features = RobustScaler().fit(frog_features)
#     pass
