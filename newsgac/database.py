from newsgac import config
from pymodm.connection import connect
db = connect(config.mongo_url, serverSelectionTimeoutMS=1000)
