#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

useradd ${JUPYTER_USER}
echo "${JUPYTER_USER}:${JUPYTER_PASSWORD}" | chpasswd
mkdir /home/${JUPYTER_USER}
chown ${JUPYTER_USER}:${JUPYTER_USER} /home/${JUPYTER_USER}
chown ${JUPYTER_USER}:${JUPYTER_USER} /notebooks

exec "$@"