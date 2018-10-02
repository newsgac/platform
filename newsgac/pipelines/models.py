from pymodm import MongoModel, fields

from newsgac.common.mixins import CreatedUpdated
from newsgac.data_sources.models import DataSource
from newsgac.learners import LearnerSVC
from newsgac.learners.models.learner import Learner
from newsgac.nlp_tools import TFIDF
from newsgac.nlp_tools.models.nlp_tool import NlpTool
from newsgac.users.models import User


class Pipeline(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    data_source = fields.ReferenceField(DataSource, required=True, blank=False)
    sw_removal = fields.BooleanField(required=True, default=True)
    lemmatization = fields.BooleanField(required=True, default=True)
    nlp_tool = fields.EmbeddedDocumentField(NlpTool, blank=True, required=True, default=TFIDF.create())
    learner = fields.EmbeddedDocumentField(Learner)

    @classmethod
    def create(cls):
        return cls(
            display_title="",
            data_source=None,
            sw_removal=cls.sw_removal.default,
            lemmatization=cls.lemmatization.default,
            nlp_tool=cls.nlp_tool.default,
            learner=LearnerSVC.create()
        )

