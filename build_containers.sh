#!/usr/bin/env bash

docker build . -t "newsgac/newsgac"
docker build . -f jupyter/Dockerfile -t "newsgac/jupyterhub"
docker build ./nginx -t newsgac/nginx