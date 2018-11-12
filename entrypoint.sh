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

function redis_ready(){
python << END
import sys
from redis import Redis
try:
    Redis(host='redis', port=6379).ping()
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

until redis_ready; do
  >&2 echo "Waiting for Redis service to come online"
  sleep 1
done &
redis_waiter_pid=$!

wait ${mongo_waiter_pid}
wait ${frog_waiter_pid}
wait ${redis_waiter_pid}

>&2 echo "FROG & Redis & MongoDB are up - continuing..."

exec "$@"