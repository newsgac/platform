# NEWSGAC
[![Build Status](https://travis-ci.org/newsgac/platform.svg?branch=master)](https://travis-ci.org/newsgac/platform)
[![Maintainability](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/maintainability)](https://codeclimate.com/github/newsgac/platform/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/test_coverage)](https://codeclimate.com/github/newsgac/platform/test_coverage)

[NEWSGAC](https://www.esciencecenter.nl/project/newsgac) is a research project which aims at transparent automatic classification of genres of newspaper articles. The project is a cooperation between the [University of Groningen](https://www.rug.nl/let/onze-faculteit/organisatie/vakgebieden/journalistiek-en-media-studies/), the Amsterdam [Center for Mathematics and Computer Science](https://www.cwi.nl/research/groups/information-access) and the [Netherlands eScience Center](https://www.esciencecenter.nl/).

In the project, we developed an online platform for applying machine learning models to text data, with the opportunity closely analyze the performance of the models. This repository contains the code of this platform.

## Setup Instructions for DOCKER

In order to run the platform at your computer, you need to have the programs [anaconda](https://www.anaconda.com/distribution/) and [docker](https://www.docker.com/products/docker-desktop) available on your system. Then execute the following commands in a command line environment:

1. git clone https://github.com/newsgac/platform.git
2. cd platform
3. docker-compose -f docker-compose_local.yml up --build

When these commands have successfully completed, the platform will be available as web server on the address: [http://localhost:5050](http://localhost:5050)

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
