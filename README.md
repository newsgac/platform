This is the development repository for NEWSGAC Project. 

NEW Setup Instructions for DOCKER

1 - Install docker-compose

2 - In terminal, navigate to newsgac_docker_dev folder.

3 - Setup MongoDB path in the docker-compose.yml line 37 to a folder of your choice on your local machine. This is to keep the database accessible locally.
For example change "/var/lib/mongodb:/data/db" to "<your_local_path>:/data/db"

4 - To run from command line, navigate to newsgac_docker_dev and run:
docker-compose up


OLD Setup Instructions

1 - Set up a virtual environment and install the requirements:
pip install -r requirements.txt

2 - Setup MongoDB. Instructions for Ubuntu here: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

3 - To run from command line, navigate to newsgac_docker_dev/flask and run:
python src/run.py

Contributors

Aysenur Bilgin (aysenur.bilgin@cwi.nl)

Erik Tjong Kim Sang (e.tjongkimsang@esciencecenter.nl)