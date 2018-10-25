from newsgac.learners.models.nb import LearnerNB
from newsgac.learners.models.svc import LearnerSVC
from newsgac.learners.models.grid_search import GridSearch

learners = [
    LearnerNB,
    LearnerSVC,
    GridSearch
]
