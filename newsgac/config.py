import logging
from os import environ, path
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

logger = logging.getLogger(__name__)


def parse_bool(value):
    return value in [True, 'true', "True", "TRUE", 1, "1", "yes", "Yes"]


if not environ.get('FLASK_ENV', False):
    logger.warn('Loading environment variables from ".env" file.')
    load_dotenv(verbose=True)

# path where this file is located, used to find relative files
root_path = path.dirname(path.abspath(__file__))
secret_key = environ.get('FLASK_SECRET_KEY')
flask_port = int(environ.get('FLASK_PORT', 5050))
mongo_host = environ.get('MONGO_HOST', 'localhost')
mongo_port = int(environ.get('MONGO_PORT', 27017))
mongo_database_name = environ.get('MONGO_DB_NAME', 'newsgac')
frog_hostname = environ.get('FROG_HOST', 'localhost')
frog_port = int(environ.get('FROG_PORT', 12345))
redis_host = environ.get('REDIS_HOST', 'localhost')
redis_port = int(environ.get('REDIS_PORT', 6379))

# celery_eager == True setting will evaluate tasks immediately, without using workers. Useful for tests
celery_eager = parse_bool(environ.get('CELERY_EAGER', False))

# number of parallel jobs (typically, this is used for internal classifier parallellization)
n_parallel_jobs = int(environ.get('N_PARALLEL_JOBS', 1))

# number of parallel jobs for cross-validation of pipelines.
# so # of concurrent jobs will be n_parallel_jobs * cross_val_n_jobs (* celery worker thread count)
# e.g. use a low value (1) on normal (laptop) hardware, otherwise we get too many jobs
n_cross_val_jobs = int(environ.get('N_CROSS_VAL_JOBS', 1))

# not used
pipeline_cache_dir = '/tmp/newsgac'

redis_url = 'redis://%s:%s/0' % (redis_host, redis_port)
mongo_url = 'mongodb://%s:%s/%s' % (mongo_host, mongo_port, mongo_database_name)

sentry_dsn = environ.get('SENTRY_DSN', None)

if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()]
    )
