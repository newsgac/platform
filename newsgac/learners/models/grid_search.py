from pymodm import fields, EmbeddedMongoModel

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    pass


class GridSearch(Learner):
    """
        This is not really a learner, but in fact a hacky placeholder to get a Grid Search choice,
        instead of directly choosing a learner. See `pipelines/grid_search.py` for the actual
        grid search implementation
    """
    name = 'Grid Search'
    tag = 'gs'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_classifier(self):
        return None
