from pymodm import fields, EmbeddedMongoModel

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    pass


class GridSearch(Learner):
    """
        This is not really a learner, but in fact a hacky placeholder to get choose a Grid Search
        Instead of directly choosing a learner.
    """
    name = 'Grid Search'
    tag = 'gs'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_classifier(self):
        return None
