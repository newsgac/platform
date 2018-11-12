import numpy
from pymodm import MongoModel, fields, EmbeddedMongoModel

from sklearn import metrics
from sklearn.metrics import confusion_matrix

from newsgac.common.fields import ObjectField
from newsgac.common.mixins import CreatedUpdated, DeleteObjectsMixin
from newsgac.learners import LearnerSVC
from newsgac.learners.models.learner import Learner
from newsgac.nlp_tools import TFIDF
from newsgac.nlp_tools.models.nlp_tool import NlpTool
from newsgac.pipelines.get_sk_pipeline import get_sk_pipeline


class Result(EmbeddedMongoModel):
    accuracy = fields.FloatField()
    cohens_kappa = fields.FloatField()
    confusion_matrix = ObjectField()
    fmeasure_macro = fields.FloatField()
    fmeasure_micro = fields.FloatField()
    fmeasure_weighted = fields.FloatField()
    precision_macro = fields.FloatField()
    precision_micro = fields.FloatField()
    precision_weighted = fields.FloatField()
    recall_macro = fields.FloatField()
    recall_micro = fields.FloatField()
    recall_weighted = fields.FloatField()
    std = fields.FloatField()

    @classmethod
    def from_prediction(cls, true_labels, predicted_labels):
        scores = numpy.array([
            1 if true_labels[i] == predicted_labels[i] else 0 for i in range(0, len(true_labels))
        ])

        return cls(
            confusion_matrix=confusion_matrix(true_labels, predicted_labels),
            # confusion_matrix=confusion_matrix(true_labels, predicted_labels, labels=DataUtils.genre_codes),
            precision_weighted=metrics.precision_score(true_labels, predicted_labels, average='weighted'),
            precision_micro=metrics.precision_score(true_labels, predicted_labels, average='micro'),
            precision_macro=metrics.precision_score(true_labels, predicted_labels, average='macro'),
            recall_weighted=metrics.recall_score(true_labels, predicted_labels, average='weighted'),
            recall_micro=metrics.recall_score(true_labels, predicted_labels, average='micro'),
            recall_macro=metrics.recall_score(true_labels, predicted_labels, average='macro'),
            fmeasure_weighted=metrics.f1_score(true_labels, predicted_labels, average='weighted'),
            fmeasure_micro=metrics.f1_score(true_labels, predicted_labels, average='micro'),
            fmeasure_macro=metrics.f1_score(true_labels, predicted_labels, average='macro'),
            cohens_kappa=metrics.cohen_kappa_score(true_labels, predicted_labels),
            accuracy=scores.mean(),
            std=scores.std()
        )


class Pipeline(CreatedUpdated, DeleteObjectsMixin, MongoModel):
    from newsgac.users.models import User
    from newsgac.data_sources.models import DataSource
    from newsgac.tasks.models import TrackedTask

    user = fields.ReferenceField(User, required=True)
    display_title = fields.CharField(required=True)
    created = fields.DateTimeField()
    updated = fields.DateTimeField()

    data_source = fields.ReferenceField(DataSource, required=True, blank=False)
    sw_removal = fields.BooleanField(required=True, default=True)
    lemmatization = fields.BooleanField(required=True, default=False)
    quote_removal = fields.BooleanField(required=True, default=True)
    nlp_tool = fields.EmbeddedDocumentField(NlpTool, blank=True, required=True, default=TFIDF.create())
    learner = fields.EmbeddedDocumentField(Learner)
    sk_pipeline = ObjectField()
    result = fields.EmbeddedDocumentField(Result)
    grid_search_result = ObjectField()

    task = fields.EmbeddedDocumentField(TrackedTask, default=TrackedTask())

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

    def get_feature_extractor(self):
        raise NotImplementedError('Subclass should implement get_feature_extractor')

    def get_sk_pipeline(self):
        return get_sk_pipeline(self)

    def delete(self):
        from newsgac.ace import ACE
        # delete this pipeline from related ace runs
        for ace in ACE.objects.raw({'pipelines': {'$in': [self.pk]}}):
            ace.delete_pipeline(self)

        super(Pipeline, self).delete()
