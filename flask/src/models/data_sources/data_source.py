import uuid
import datetime

import src.models.data_sources.constants as DataSourceConstants
import src.models.data_sources.errors as DataSourceErrors
from src.data_engineering.feature_extraction import Article
from src.common.database import Database
import src.common.utils as Utilities
import re
from bson import ObjectId
import src.data_engineering.utils as DataUtils

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

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(DataSourceConstants.COLLECTION, {"_id": id}))

    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email})]

    @classmethod
    def get_processed_datasets(cls):
        return [cls(**elem) for elem in DATABASE.find(DataSourceConstants.COLLECTION, {"processing_completed": {"$ne": None}})]

    @classmethod
    def get_processed_by_user_email(cls, user_email):
        return [cls(**elem) for elem in
                DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email, "processing_completed": {"$ne": None}})]

    @classmethod
    def get_by_user_email_and_display_title(cls, user_email, display_title):
        return cls(**DATABASE.find_one(DataSourceConstants.COLLECTION, {"user_email": user_email,
                                                                        "display_title": display_title}))

    @staticmethod
    def get_titles_by_user_email(user_email, processed=False):
        ds_list = DataSource.get_by_user_email(user_email=user_email)
        titles = []
        for ds in ds_list:
            if processed and ds.processing_started is not None and ds.processing_completed is not None:
                titles.append(ds.display_title)
            elif not processed:
                titles.append(ds.display_title)

        return titles

    @staticmethod
    def is_source_unique(user_email, display_title, filename):
        user_data_list = DataSource.get_by_user_email(user_email)

        for ds in user_data_list:
            if ds.user_email == user_email and ds.display_title == display_title:
                raise DataSourceErrors.ResourceDisplayTitleAlreadyExistsError("The display title is already taken.")
            elif ds.user_email == user_email and ds.secure_filename == filename:
                raise DataSourceErrors.ResourceFilenameAlreadyExistsError("Another file with the same name already exists.")

        return True

    def save_to_db(self):
        DATABASE.update(DataSourceConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def process_data_source(self):
        self.processing_started = datetime.datetime.utcnow()
        self.save_to_db()

        # process rather raw version and upload
        structured_data = self.read_and_upload_raw_text_input_file()

        # add features separately
        articles_from_db = DataSource.get_articles_by_data_source(self._id)
        print "retrieved articles from db"
        print len(articles_from_db)

        for article in articles_from_db:
            art_id = article['_id']
            art = Article(text=article['article_raw_text'])
            self.add_features_to_db(article_id=art_id, dict=art.get_features_frog())

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
    def get_processed_article_by_id(id):
        return DATABASE.find_one(DataSourceConstants.COLLECTION_PROCESSED, {"_id": ObjectId(id)})

    @staticmethod
    def is_allowed(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_raw_to_db(self, dict):
        DATABASE.insert(DataSourceConstants.COLLECTION_PROCESSED, dict)

    @staticmethod
    def get_articles_by_data_source(data_source_id):
        return [elem for elem in DATABASE.find(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": data_source_id})]

    def add_features_to_db(self, article_id, dict):
        DATABASE.update(DataSourceConstants.COLLECTION_PROCESSED, {'_id': article_id, 'data_source_id': self._id}, {'$set': dict})

    def read_and_upload_raw_text_input_file(self):

        file = DATABASE.getGridFS().get(self.file_handler_db).read()
        data = []

        limit = 100
        for line in file.splitlines():
            line = line.rstrip()

            # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+) ((?s).*)$', line).groups()
            # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+[^&]) ((?s).*)$', line).groups()
            groups = re.search(r'^__label__(.{3}.+)DATE\=(.{8}) ((?s).*)$', line).groups()

            if not groups:
                groups = re.search(r'^__label__(.{3})((?s).*)', line).groups()
                label = groups[0].rstrip()
                date = None
                raw_text = groups[1].rstrip()
            else:
                label = groups[0].rstrip()
                date_str = groups[1].rstrip()
                # TODO: Need to test the following
                day = date_str.split("/")[0]
                month = date_str.split("/")[1]
                year = date_str.split("/")[2]
                # fix for conversion 20xx where xx < 69 although the data is from 1900s
                date_str_corr = day + "/" + month + "/19" + year
                print date_str_corr
                date = datetime.datetime.strptime(date_str_corr, "%d/%m/%Y").strftime("%d-%m-%Y")
                raw_text = groups[2].rstrip()

            row = dict(data_source_id=self._id, genre_friendly=DataUtils.genre_codebook_friendly[label], genre=DataUtils.genre_codebook[label], date=date, article_raw_text=raw_text)
            self.save_raw_to_db(row)
            data.append(row)

            if limit < 1:
                break
            else:
                limit -= 1

        return data

    def get_number_of_instances(self):
        return DATABASE.get_count(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": self._id})



