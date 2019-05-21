# NEWSGAC
[![Build Status](https://travis-ci.org/newsgac/platform.svg?branch=master)](https://travis-ci.org/newsgac/platform)
[![Maintainability](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/maintainability)](https://codeclimate.com/github/newsgac/platform/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/test_coverage)](https://codeclimate.com/github/newsgac/platform/test_coverage)

This is the development repository for NEWSGAC Project.

## Setup Instructions for DOCKER

1. Install docker-compose

2. In terminal, navigate to platform folder.

3. By default, database data will be saved to `./../data`, e.g. in a folder called `data` in the parent of this repository's directory.
   To change this modify `docker-compose_local.yml` line 43 to a folder of your choice on your local machine.
   For example change `./../data:/data/db` to `<your_local_path>:/data/db`

4. To run from command line, navigate to platform and run:

```
docker-compose -f docker-compose_local.yml up --build
```

The platform will now be available as web server on: 
http://localhost:5050

## Run flask web app locally (through IDE)

You might want to run flask outside of Docker (because it is e.g. easier to attach a debugger).

* Follow `Setup Instructions for DOCKER` instructions so that all services are online (Mongo, Redis, FROG, celery workers).
* Make sure the flask docker container is DOWN:

```
docker-compose -f docker-compose_local.yml stop web
```

* Set up a virtual environment (python 2.7) and install the requirements:

```
pip install -r requirements.txt
```

* Setup the correct environmental variables (`.env.local`) e.g. by running

```
export $(cat .env.local | xargs)
```

* To run from command line, navigate to `platform/` and run:

```
PYTHONPATH=. python newsgac/app.py
```
* The local web server will be running on `http://localhost:5050`.

## Debugging tasks

Typically tasks are executed by celery workers. If you want to debug a task you can do one of two things:

1. Run a celery worker in debug mode
2. In `config.py`, set `celery_eager` to True. This will cause celery to
   run tasks in the main thread instead of offloading it to workers.


## Running the tests (Docker)
1. `docker-compose -f docker-compose_test.yml build test`
2. `docker-compose -f docker-compose_test.yml run test`
3. `docker-compose -f docker-compose_test.yml down`

## Running the tests (Local)
* Setup local (virtual) environment as when running flask locally

* Load the test env vars:

```
export $(cat .env.test | xargs)
```

* Make sure the database, Frog and redis are running (e.g. `docker-compose -f docker-compose_local.yml up database redis frog`

* Run tests using

```
pytest .
```


## Python console

E.g. to create a user:

* Start console using docker-compose (or from you local environment using `python`):

```
docker-compose -f docker-compose_local.yml run web python
```

* Import database & user model

```
from newsgac import database
from newsgac.users.models import User
```

* Create new user

```
u = User(email='testuser@test.com', password='testtest', name='Test', surname='User')
u.save()
```

* You can now login from the frontend as this user.

## References

[Utilizing a Transparency-driven Environment toward Trusted Automatic Genre Classification: A Case Study in Journalism History](https://arxiv.org/pdf/1810.00968.pdf)

```
@inproceedings{bilgin2018utilizing,
  title={Utilizing a Transparency-driven Environment toward Trusted Automatic Genre Classification: A Case Study in Journalism History},
  author={Bilgin, Aysenur and Sang, Erik Tjong Kim and Smeenk, Kim and Hollink, Laura and van Ossenbruggen, Jacco and Harbers, Frank and Broersma, Marcel},
  booktitle={2018 IEEE 14th International Conference on e-Science (e-Science)},
  pages={486--496},
  year={2018},
  organization={IEEE}
}
```

## Contributors

- Aysenur Bilgin (aysenur.bilgin@cwi.nl)
- Erik Tjong Kim Sang (e.tjongkimsang@esciencecenter.nl)
- Tom Klaver (t.klaver@esciencecenter.nl)
