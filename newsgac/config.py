from os import environ, path


class Env:
    local = 'local'
    localdocker = 'localdocker'
    test = 'test'
    production = 'production'


root_path = path.dirname(path.abspath(__file__))

environment = environ['ENVIRONMENT']
secret_key = environ['FLASK_SECRET_KEY']

flask_port = 5000
# celery_eager setting will evaluate tasks immediately, without using workers.
celery_eager = False
mongo_host = 'database'
mongo_port = 27017
mongo_database_name = 'newsgacdev'

frog_hostname = 'frog'
frog_port = 12345
redis_host = 'redis'
redis_port = 6379

n_parallel_jobs = 8
pipeline_cache_dir = '/tmp/newsgac'

if environment in [Env.local, Env.test]:
    flask_port = 5050
    celery_eager = False
    mongo_host = 'localhost'
    frog_hostname = 'localhost'
    redis_host = 'localhost'

if environment == Env.test:
    mongo_database_name = 'newsgactest'
    celery_eager = True


redis_url = 'redis://%s:%s/0' % (redis_host, redis_port)
mongo_url = 'mongodb://%s:%s/%s' % (mongo_host, mongo_port, mongo_database_name)
