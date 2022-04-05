# NEWSGAC

[![DOI](https://zenodo.org/badge/161313748.svg)](https://zenodo.org/badge/latestdoi/161313748)
[![Build Status](https://travis-ci.org/newsgac/platform.svg?branch=master)](https://travis-ci.org/newsgac/platform)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7da69edab6084303a6bbad203013b5a2)](https://www.codacy.com/manual/eriktks/platform?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=newsgac/platform&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/maintainability)](https://codeclimate.com/github/newsgac/platform/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/40ee8b8ba037d26a4e4d/test_coverage)](https://codeclimate.com/github/newsgac/platform/test_coverage)

[NEWSGAC](https://www.esciencecenter.nl/project/newsgac) is a research project which aims at transparent automatic classification of genres of newspaper articles. The project is a cooperation between the [University of Groningen](https://www.rug.nl/let/onze-faculteit/organisatie/vakgebieden/journalistiek-en-media-studies/), the Amsterdam [Center for Mathematics and Computer Science](https://www.cwi.nl/research/groups/human-centered-data-analytics) and the [Netherlands eScience Center](https://www.esciencecenter.nl/).

In the project, we developed an online platform for applying machine learning models to text data, with the opportunity to closely analyze the performance of the models. This repository contains the code of this platform.

## Setup Instructions

In order to run the platform at your computer, you need to have [docker](https://www.docker.com/products/docker-desktop) available on your system. Then execute the following commands in a command line environment (instructions for Linux):

 1. `git clone https://github.com/newsgac/platform.git`
 2. `cd platform`
 3. `docker build . -t "newsgac/newsgac"`
 4. `export $(egrep -v '^#' .env.default | xargs)`
 5. `docker stack deploy -c docker-compose.yml -c docker-compose.dev.yml newsgacdev`

When these commands have successfully completed, the platform will be available as a web server on the address: [http://YOUR-IP-ADDRESS:5050](http://YOUR-IP-ADDRESS:5050)

Steps 1, 2 and 3 need to be executed only once for installing the system.
Both step 4 and step 5 are required each time when you start the system.

Optional steps:

 * For adaption to local environment: edit file .env.default or create your own version
 * For Jupyter notebook support: `docker build . -f jupyter/Dockerfile -t "newsgac/jupyterhub"`
 * During production: `docker build ./nginx -t newsgac/nginx`
 * installation instructions for usage of a [kubernetes cluster](k8s/README.md) (CLARIAH)

Stopping the system:

 * `docker service rm newsgacdev_database newsgacdev_frog newsgacdev_frogworker newsgacdev_redis newsgacdev_web newsgacdev_worker`

Note that it takes a few seconds to completely stop all parts of the system.


## Run flask web app locally (through IDE)

You might want to run flask outside of Docker (because it is e.g. easier to attach a debugger).

  * Follow `Setup Instructions for DOCKER` instructions so that all services are online (Mongo, Redis, FROG, celery workers).
  * Make sure the flask docker container is DOWN:

```
    docker service rm newsgacdev_web
```

  * Set up a virtual environment (python 3.7) and install the requirements:

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
 2. Make sure `CELERY_EAGER=True` (or unset). This will cause celery to run tasks in the main thread instead of offloading it to workers.

### Access logs
- Web console
    - Find the web container with `docker ps`
    - Read the logs with `docker logs newsgacdev_web.[many_numbers]` (use tab completion), search for PIN
- Crash logs
    - Find the worker container with `docker ps`
    - Read the logs with `docker logs newsgacdev_worker.[many_numbers]` (use tab completion)
- Brief model crash logs
    - Mouse-over the Status.FAILURE field in the Pipelines page

## Running the tests (Docker)

 1. `docker run --name=mongo -it --rm -d mongo`
 2. 
```
    docker run \
        --name=newsgactest \
        -it \
        --network=container:mongo \
        --mount type=bind,src="$(pwd)"/newsgac,destination=/newsgac/newsgac \
        --entrypoint=sh \
        newsgac/newsgac -c pytest --cov=newsgac --cov-report=xml
```
 3. `docker stop newsgactest mongo`

## Running the tests (Local)

  * Setup local (virtual) environment as when running flask locally
  * Load the test env vars:

```
    export $(cat .env.test | xargs)
```

  * Make sure the database, Frog and redis are running (e.g. `docker stack deploy -c docker-compose.yml -c docker-compose.dev.yml newsgacdev`
  * Load env variables, then run tests using

```
    pytest .
```

## Python console

E.g. to create a user:

  * Start console using docker (or from you local environment using `python`):

```
    docker exec -it newsgac_dev web python
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
  
## Useful commands
 - `docker stack ps newsgacdev`
 - `docker service ps newsgacdev_worker`
 - `docker service inspect newsgacdev_worker`
 - `docker service logs newsgacdev_worker`

## References

A. Bilgin, E. Tjong Kim Sang, K. Smeenk, L. Hollink, J. van Ossenbruggen, F. Harbers and M. Broersma, [Utilizing a Transparency-driven Environment toward Trusted Automatic Genre Classification: A Case Study in Journalism History](https://arxiv.org/pdf/1810.00968.pdf) (2018)

```
@inproceedings{bilgin2018utilizing,
   title={Utilizing a Transparency-driven Environment toward Trusted Automatic Genre Classification: A Case Study in Journalism History},
   author={Bilgin, Aysenur and Tjong Kim Sang, Erik and Smeenk, Kim and Hollink, Laura and van Ossenbruggen, Jacco and Harbers, Frank and Broersma, Marcel},
   booktitle={2018 IEEE 14th International Conference on e-Science (e-Science)},
   pages={486--496},
   year={2018},
   organization={IEEE}
}
```

K. Smeenk, A. Bilgin, T. Klaver, E. Tjong Kim Sang, L. Hollink, J. van Ossenbruggen, F. Harbers and M. Broersma, [Grounding Paradigmatic Shifts In Newspaper Reporting In Big Data. Analysing Journalism History By Using Transparent Automatic Genre Classification](https://ifarm.nl/erikt/papers/2019dh.pdf) (2019)

```
@inproceedings{smeenk2019dh,
   author     = "Kim Smeenk and Aysenur Bilgin and Tom Klaver and Erik Tjong Kim Sang and Laura Hollink and Jacco van Ossenbruggen and Frank Harbers and Marcel Broersma",
   title      = "{Grounding Paradigmatic Shifts In Newspaper Reporting In Big Data. Analysing Journalism History By Using Transparent Automatic Genre Classification}",
   booktitle  = "{Digital Humanities Conference 2019 (DH2019)}",
   publisher  = "{Utrecht, The Netherlands}",
   year       = "2019"
}
```

T. Klaver, E. Tjong Kim Sang, A. Bilgin, K. Smeenk, L. Hollink, J. van Ossenbruggen, F. Harbers and M. Broersma, [Introducing a transparency-driven platform for creating, comparing and explaining machine learning pipelines](https://ifarm.nl/erikt/papers/2019-ictopen.pdf) (2019)

```
@inproceedings{klaver2019ictopen,
   author     = "Tom Klaver and Erik Tjong Kim Sang and Aysenur Bilgin and Kim Smeenk and Laura Hollink and Jacco van Ossenbruggen and Frank Harbers and Marcel Broersma",
   title      = "{Introducing a transparency-driven platform forcreating, comparing and explaining machinelearning pipelines}",
   booktitle  = "{ICT-Open}",
   publisher  = "{Hilversum, The Netherlands}",
   year       = "2019",
   note       = "(demo presentation abstract)"
}
```

## Contributors

  * Aysenur Bilgin (aysenur.bilgin@cwi.nl)
  * Erik Tjong Kim Sang (e.tjongkimsang@esciencecenter.nl)
  * Tom Klaver (t.klaver@esciencecenter.nl)
