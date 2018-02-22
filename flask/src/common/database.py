import gridfs
import pymongo
from src.app import app

__author__ = 'abilgin'

class Database(object):

    def __init__(self):
        if app.DOCKER_RUN:
            self.URI = "mongodb://database:27017"  # use this when dockerized
        else:
            self.URI = "mongodb://127.0.0.1:27017"

        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client["newsgacdev"]
        self.fs = gridfs.GridFS(self.db)

    def insert(self, collection, data):
        self.db[collection].insert(data)

    def find(self, collection, query):
        return self.db[collection].find(query).sort("_id", pymongo.ASCENDING)

    def find_one(self, collection, query):
        return self.db[collection].find_one(query)

    def get_count(self, collection, query):
        return self.db[collection].find(query).count()

    def update(self, collection, query, data):
        self.db[collection].update(query, data, upsert=True)

    def remove(self, collection, query):
        self.db[collection].remove(query)

    def iter_collection(self, collection, key={}):
        """Creates a cursor to iterate over and returns it
        a key can be given to limit the results from the find command
        """
        cursor = self.db[collection].find(key, no_cursor_timeout=True)
        for item in cursor:
            yield item
        cursor.close()

    def getGridFS(self):
        return self.fs