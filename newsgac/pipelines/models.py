import itertools
import operator

from enum import Enum
from pymodm import MongoModel, EmbeddedMongoModel, fields

from newsgac.common.fields import EnumField
from newsgac.common.mixins import CreatedUpdated
from newsgac.learners import LearnerSVC
from newsgac.learners.models.learner import Learner
from newsgac.tasks.models import TrackedTask, Status
from newsgac.users.models import User
from newsgac.data_engineering.utils import features

import newsgac.data_engineering.utils as DataUtils


class NlpTool(Enum):
    FROG = 'frog'
    SPACY = 'spacy'
    TFIDF = 'tf-idf'


def nlp_tool_readable(tool):
    return {
        NlpTool.FROG: 'Frog',
        NlpTool.SPACY: 'Spacy',
        NlpTool.TFIDF: 'TF-IDF',
    }[NlpTool(tool)]


class PreProcessor(EmbeddedMongoModel):
    sw_removal = fields.BooleanField(required=True, default=True)
    lemmatization = fields.BooleanField(required=True, default=True)
    nlp_tool = EnumField(required=True, choices=NlpTool)
    scaling = fields.BooleanField(required=True, default=True)
    features = fields.DictField(default={feature: True for feature in features})

    @classmethod
    def create(cls):
        return cls(
            sw_removal=cls.sw_removal.default,
            lemmatization=cls.lemmatization.default,
            nlp_tool=NlpTool.TFIDF,
            scaling=cls.scaling.default,
            features=cls.features.default
        )


class Pipeline(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    pre_processor = fields.EmbeddedDocumentField(PreProcessor)
    learner = fields.EmbeddedDocumentField(Learner)

    @classmethod
    def create(cls):
        return cls(
            display_title="",
            pre_processor = PreProcessor.create(),
            learner = LearnerSVC.create()
        )
