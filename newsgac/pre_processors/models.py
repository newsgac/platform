import itertools
import operator

from pymodm import MongoModel, EmbeddedMongoModel, fields

from newsgac.common.mixins import CreatedUpdated
from newsgac.tasks.models import TrackedTask, Status
from newsgac.users.models import User
from newsgac.data_engineering.utils import features

import newsgac.data_engineering.utils as DataUtils


class PreProcessor(CreatedUpdated, MongoModel):
    # configuration options:
    # OCR
    # Stop word removal
    # Lemmatization / Stemming
    # Vectorizer (FROG / TF-IDF)
    # scaling
    # caching?

    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    # description = fields.CharField(required=True)
    sw_removal = fields.BooleanField(required=True, default=True)
    lemmatization = fields.BooleanField(required=True, default=True)
    nlp_tool = fields.CharField(required=True, default="tf-idf", choices=["frog", "spacy", "tf-idf"])
    scaling = fields.BooleanField(required=True, default=True)
    features = fields.ListField(fields.CharField(choices=features), blank=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    @classmethod
    def create(cls):
        return cls(
            display_title="",
            sw_removal=cls.sw_removal.default,
            lemmatization=cls.lemmatization.default,
            nlp_tool=None,
            scaling=cls.scaling.default,
            features=[]
        )


