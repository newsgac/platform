#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

function mongo_ready(){
python << END
import sys
import pymongo
try:
    client = pymongo.MongoClient('mongodb://database:27017', serverSelectionTimeoutMS=1000)
    client.server_info()
except:
    sys.exit(-1)
sys.exit(0)
END
}

function frog_ready(){
python << END
import sys
from pynlpl.clients.frogclient import FrogClient
try:
    frogclient = FrogClient('frog', 12345, returnall=True)
except:
    sys.exit(-1)
sys.exit(0)
END
}

function rabbitmq_ready(){
python << END
from kombu import Connection
import sys
#from celery import Celery
try:
    conn = Connection('amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbit//', transport_options={
        'visibility_timeout': 1000,
    })
    conn.ensure_connection(max_retries=1)
except:
    sys.exit(-1)
sys.exit(0)
END
}

until mongo_ready; do
  >&2 echo "Waiting for MongoDB to come online"
  sleep 1
done &
mongo_waiter_pid=$!

until frog_ready; do
  >&2 echo "Waiting for FROG service to come online"
  sleep 1
done &
frog_waiter_pid=$!

until rabbitmq_ready; do
  >&2 echo "Waiting for RabbitMQ service to come online"
  sleep 1
done &
rabbitmq_waiter_pid=$!

wait ${mongo_waiter_pid}
wait ${frog_waiter_pid}
wait ${rabbitmq_waiter_pid}

>&2 echo "FROG & RabbitMQ & MongoDB are up - continuing..."

exec "$@"