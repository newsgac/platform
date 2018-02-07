import uuid

import datetime

import src.models.data_sources.constants as DataSourceConstants
import src.models.data_sources.errors as DataSourceErrors
from data_engineering.feature_extraction import Article
from src.common.database import Database
import src.common.utils as Utilities
import src.data_engineering.data_io as io

UT = Utilities.Utils()
DATABASE = Database()
ALLOWED_EXTENSIONS = {'txt', 'csv'}

__author__ = 'abilgin'

class DataSource(object):

    def __init__(self, user_email, display_title, description, secure_filename, **kwargs):

        if 'new_handler' in kwargs:
            # creation from the web
            self.user_email = user_email
            self._id = uuid.uuid4().hex
            self.created = datetime.datetime.utcnow()
            self.processing_started = None
            self.processing_completed = None
            self.file_handler_db = kwargs['new_handler']
        else:
            # default constructor from the database
            self.__dict__.update(kwargs)

        self.user_email = user_email
        self.display_title = display_title
        self.description = description
        self.secure_filename = secure_filename

    def __eq__(self, user_email, display_title, description, filename):

        return self.user_email == user_email and self.display_title == display_title \
                and self.description == description and self.secure_filename == filename

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(DataSourceConstants.COLLECTION, {"_id": id}))

    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email})]

    @staticmethod
    def is_source_unique(user_email, display_title, description, filename):
        user_data_list = DataSource.get_by_user_email(user_email)

        for ds in user_data_list:
            if ds.__eq__(user_email, display_title, description, filename):
                raise DataSourceErrors.ResourceAlreadyExistsError("The data source already exists.")

        return True

    def save_to_db(self):
        DATABASE.update(DataSourceConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def process_data_source(self):
        self.processing_started = datetime.datetime.utcnow()
        self.save_to_db()

        # process rather raw version and upload
        structured_data = io.read_and_upload_raw_text_input_file(self)

        # add features separately
        articles_from_db = self.get_articles_by_data_source()
        print "retrieved articles from db"
        print len(articles_from_db)

        for article in articles_from_db:
            art_id = article['_id']
            art = Article(text=article['article_raw_text'])
            self.add_features_to_db(article_id=art_id, dict=art.get_features())

        self.processing_completed = datetime.datetime.utcnow()
        self.save_to_db()

    def delete(self):
        DATABASE.remove(DataSourceConstants.COLLECTION, {"_id": self._id})
        DATABASE.remove(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": self._id})
        DATABASE.getGridFS().delete(self.file_handler_db)

    def get_user_friendly_created(self):
        return UT.get_local_display_time(self.created)

    def get_user_friendly_processing_started(self):
        return UT.get_local_display_time(self.processing_started)

    def get_user_friendly_processing_finished(self):
        return UT.get_local_display_time(self.processing_completed)

    def get_processing_duration(self):
        delta = self.processing_completed - self.processing_started
        m, s = divmod(delta.seconds, 60)
        h, m = divmod(m, 60)
        if int(h) == 0:
            return "{:2d} minutes {:2d} seconds".format(int(m), int(s))

        return "{:2d} hours {:2d} minutes {:2d} seconds".format(int(h), int(m), int(s))

    @staticmethod
    def is_allowed(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_raw_to_db(self, dict):
        DATABASE.insert(DataSourceConstants.COLLECTION_PROCESSED, dict)

    def get_articles_by_data_source(self):
        return [elem for elem in DATABASE.find(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": self._id})]

    def add_features_to_db(self, article_id, dict):
        DATABASE.update(DataSourceConstants.COLLECTION_PROCESSED, {'_id': article_id, 'data_source_id': self._id}, {'$set': dict})




