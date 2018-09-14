import itertools
import operator

from enum import Enum
from pymodm import MongoModel, EmbeddedMongoModel, fields

from newsgac.common.fields import EnumField
from newsgac.common.mixins import CreatedUpdated
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


class PreProcessor(CreatedUpdated, MongoModel):
    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    sw_removal = fields.BooleanField(required=True, default=True)
    lemmatization = fields.BooleanField(required=True, default=True)
    nlp_tool = EnumField(required=True, choices=NlpTool)
    scaling = fields.BooleanField(required=True, default=True)
    features = fields.DictField(default={feature: True for feature in features})
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    @classmethod
    def create(cls):
        return cls(
            display_title="",
            sw_removal=cls.sw_removal.default,
            lemmatization=cls.lemmatization.default,
            nlp_tool=NlpTool.TFIDF,
            scaling=cls.scaling.default,
            features=cls.features.default
        )


