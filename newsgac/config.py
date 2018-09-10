from os import environ


class Env:
    local = 'local'
    localdocker = 'localdocker'
    test = 'test'
    production = 'production'


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
rabbitmq_url = 'amqp://%s:%s@rabbit//' % (environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])

if environment in [Env.local, Env.test]:
    flask_port = 5050
    celery_eager = False
    mongo_host = 'localhost'
    frog_hostname = 'localhost'
    rabbitmq_url = 'amqp://%s:%s@localhost//' % (environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])

if environment == Env.test:
    mongo_database_name = 'newsgactest'
    celery_eager = True




mongo_url = 'mongodb://%s:%s/%s' % (mongo_host, mongo_port, mongo_database_name)
