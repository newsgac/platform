from gridfs import GridFS, GridFSBucket

from newsgac import config

from newsgac.common.database import Database
DATABASE = Database()


from pymodm.connection import connect
db = connect(config.mongo_url)
# gridfs = GridFS(db)
# gridfs_bucket = GridFSBucket(gridfs)
