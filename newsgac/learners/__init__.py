from newsgac.learners.models.nb import LearnerNB
from newsgac.learners.models.svc import LearnerSVC
from newsgac.learners.models.grid_search import GridSearch
from newsgac.learners.models.rf import LearnerRF
from newsgac.learners.models.gb import LearnerGB
from newsgac.learners.models.xgb import LearnerXGB

learners = [
    LearnerNB,
    LearnerSVC,
    LearnerRF,
    LearnerGB,
    LearnerXGB,
    GridSearch
]
