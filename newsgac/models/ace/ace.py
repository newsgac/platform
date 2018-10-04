import datetime
import uuid

import pymongo

# from newsgac.models.data_sources.data_source_old import DataSource
from newsgac.models.experiments.factory import get_experiment_by_id
from newsgac.visualisation.comparison import ExperimentComparator
from . import constants
from newsgac.database import DATABASE

__author__ = 'tom'

class Ace(object):
    collection = constants.COLLECTION
    @classmethod
    def create(cls, experiments, user_email=None, *args, **kwargs):
        ace = cls()
        ace._id = uuid.uuid4().hex
        ace.created = datetime.datetime.utcnow()
        ace.user_email = user_email
        ace.experiments = map(lambda e: e._id, experiments)
        ace.result = None
        ace.__dict__.update(kwargs)
        return ace

    @classmethod
    def get_by_id(cls, id):
        task = cls()
        task.__dict__.update(**DATABASE.find_one(constants.COLLECTION, {"_id": id}))
        return task

    @classmethod
    def find_one(cls, criteria):
        task = cls()
        task.__dict__.update(**DATABASE.find_one(constants.COLLECTION, criteria))
        return task

    @classmethod
    def get_all(cls):
        return list(DATABASE.find(constants.COLLECTION, {}))

    @classmethod
    def get_all_by_user_email(cls, user_email):
        return list(DATABASE.find(constants.COLLECTION, {'user_email': user_email}).sort('created', pymongo.DESCENDING))[:5]

    def save_to_db(self):
        DATABASE.update(constants.COLLECTION, {"_id": self._id}, self.__dict__)

    def run(self):
        processed_data_source_list = DataSource.get_processed_datasets()
        experiment_ds_dict = {}
        text_explanation_experiments = []
        # used_data_source_ids = Experiment.get_used_data_sources_for_public()

        experiments = map(lambda e: get_experiment_by_id(e), self.experiments)
        comparator = ExperimentComparator(experiments)
        # get the test articles
        test_articles_genres = comparator.retrieveUniqueTestArticleGenreTuplesBasedOnRawText()
        tabular_data_dict, combinations = comparator.generateAgreementOverview(test_articles_genres)

        def group_by_attr(iterable, attr):
            from operator import itemgetter
            from itertools import groupby
            return { k: list(v) for k,v in groupby(sorted(iterable, key=itemgetter(attr)), key=itemgetter(attr)) }

        grouped_tabular_data = group_by_attr(tabular_data_dict, 'article_number')

        # prepare data, what we want to show is:
        # article (text, datasource(s)
        data = dict(data_sources_db=processed_data_source_list,
                       experiment_ds_dict = experiment_ds_dict,
                       text_explanation_experiments=text_explanation_experiments,
                       articles=test_articles_genres,
                       tabular_data_dict=tabular_data_dict,
                       combinations=combinations,
                       mimetype='text/html',
                       grouped_tabular_data=grouped_tabular_data)

        # pickled_data = dill.dumps(data)
        # import sys
        # size = sys.getsizeof(pickled_data)

        self.result = DATABASE.save_object(data)
        self.save_to_db()

        # return render_template('experiments/analyse_compare_explain.html',
        #                data_sources_db=processed_data_source_list,
        #                experiment_ds_dict = experiment_ds_dict,
        #                text_explanation_experiments=text_explanation_experiments,
        #                articles=test_articles_genres,
        #                tabular_data_dict=tabular_data_dict,
        #                combinations=combinations,
        #                mimetype='text/html',
        #                grouped_tabular_data=grouped_tabular_data
        #                        )

    # return render_template('experiments/analyse_compare_explain.html', data_sources_db=processed_data_source_list, experiment_ds_dict = experiment_ds_dict)
