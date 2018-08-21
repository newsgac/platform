# NEWSGAC

This is the development repository for NEWSGAC Project.

## Setup Instructions for DOCKER

1. Install docker-compose

2. In terminal, navigate to newsgac_docker_dev folder.

3. By default, database data will be saved to `./../data`, e.g. in a folder called `data` in the parent of this repository's directory.
   To change this modify `docker-compose_local.yml` line 22 to a folder of your choice on your local machine.
   For example change `./../data:/data/db` to `<your_local_path>:/data/db`

4. To run from command line, navigate to newsgac_docker_dev and run:

   ```
   docker-compose -f docker-compose.yml -f docker-compose_local.yml up --build
   ```


## Run flask web app locally

You might want to run flask outside of Docker (because it is e.g. easier to attach a debugger).

1. Follow `Setup Instructions for DOCKER` instructions so that all services are online (Mongo, RabbitMQ, FROG, celery workers).

2. Set up a virtual environment and install the requirements:

   ```
   pip install -r requirements.txt
   ```

3. Setup the correct environmental variables (`.env.local`) e.g. by running
   ```
   export $(cat .env.local | xargs)
   ```

4. To run from command line, navigate to `newsgac_docker_dev/flask` and run:
   ```
   python src/app.py
   ```

5. The local web server will be running on `http://localhost:5050`, the Docker server on `http://localhost:5000`.

## Contributors

- Aysenur Bilgin (aysenur.bilgin@cwi.nl)
- Erik Tjong Kim Sang (e.tjongkimsang@esciencecenter.nl)
- Tom Klaver (t.klaver@esciencecenter.nl)