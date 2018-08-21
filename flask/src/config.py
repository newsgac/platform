from os import environ
from enum import Enum


class Env(Enum):
    local = 'local'
    localdocker = 'localdocker'
    test = 'test'
    production = 'production'


environment = environ['ENVIRONMENT']
secret_key = environ['FLASK_SECRET_KEY']

celery_eager = False
mongo_url = 'mongodb://database:27017'
frog_hostname = 'frog'
frog_port = 12345
rabbitmq_url = 'amqp://%s:%s@rabbit//' % (environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])

if environment == Env.local:
    celery_eager = True
    mongo_url = 'mongodb://localhost:27017'
    frog_hostname = 'localhost'
    rabbitmq_url = 'amqp://%s:%s@localhost//' % (environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])