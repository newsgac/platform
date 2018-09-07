import gridfs
import pymongo
from dill import dill

from newsgac import config

__author__ = 'abilgin'

class Database(object):

    def __init__(self):
        self.URI = config.mongo_url

        self.client = pymongo.MongoClient(self.URI, connectTimeoutMS=1000, serverSelectionTimeoutMS=1000)
        self.db = self.client[config.mongo_database_name]
        self.fs = gridfs.GridFS(self.db)

        self.db['predictions'].create_index([("article_text", "text")])

        self.object_cache = {}

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

    def updateManyForRemoval(self, collection, key):
        self.db[collection].update_many({}, {'$unset': {key: 1}})

    def remove(self, collection, query):
        self.db[collection].remove(query)

    def iter_collection(self, collection, key={}):
        """Creates a cursor to iterate over and returns it
        a key can be given to limit the results from the find command
        """
        cursor = self.db[collection].find(key, no_cursor_timeout=True).sort("_id", pymongo.ASCENDING)
        for item in cursor:
            yield item
        cursor.close()

    def getGridFS(self):
        return self.fs

    def save_object(self, obj, cache=False):
        ref = self.fs.put(dill.dumps(obj))
        if cache:
            self.object_cache[ref] = obj
        return ref

    def load_object(self, ref, cache=True, unpickle=True):
        if ref in self.object_cache.keys():
            return self.object_cache[ref]
        else:
            obj = self.fs.get(ref).read()
            if unpickle:
                obj = dill.loads(obj)
            if cache:
                self.object_cache[ref] = obj
            return obj