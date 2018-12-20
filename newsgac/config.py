from os import environ, path


class Env:
    local = 'local'
    localdocker = 'localdocker'
    test = 'test'
    dockertest = 'dockertest'
    production = 'production'


# one of Env.
environment = environ['ENVIRONMENT']
assert environment in Env.__dict__

# path where this file is located, used to find relative files
root_path = path.dirname(path.abspath(__file__))

secret_key = environ['FLASK_SECRET_KEY']

flask_port = 5050

mongo_host = 'database'
mongo_port = 27017
mongo_database_name = 'newsgacdev'

frog_hostname = 'frog'
frog_port = 12345
redis_host = 'redis'
redis_port = 6379

# celery_eager == True setting will evaluate tasks immediately, without using workers.
celery_eager = False

# number of parallel jobs (typically, this is used for internal classifier parallellization)
n_parallel_jobs = 8

# number of parallel jobs for cross-validation of pipelines.
# so # of concurrent jobs will be n_parallel_jobs * cross_val_n_jobs (* celery worker thread count)
# e.g. use a low value (1) on normal (laptop) hardware, otherwise we get too many jobs
cross_val_n_jobs = 1

# not used
pipeline_cache_dir = '/tmp/newsgac'


if environment in [Env.production]:
    cross_val_n_jobs = 8


if environment in [Env.local, Env.test]:
    mongo_host = 'localhost'
    frog_hostname = 'localhost'
    redis_host = 'localhost'


if environment in [Env.test, Env.dockertest]:
    mongo_database_name = 'newsgactest'
    celery_eager = True


redis_url = 'redis://%s:%s/0' % (redis_host, redis_port)
mongo_url = 'mongodb://%s:%s/%s' % (mongo_host, mongo_port, mongo_database_name)
