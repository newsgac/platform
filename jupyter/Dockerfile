FROM jupyterhub/jupyterhub:2.1

ARG NODEJS_VERSION=16
ARG PYTHON_VERSION=3.9.10

RUN apt-get update && apt install -y \
        build-essential \
        curl \
        git \
        libffi-dev \
        libmariadb-dev-compat \
        libsqlite3-dev

# set up repo for nodejs 16
# (necessary for jupyterlab hub-extension)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODEJS_VERSION}.x | bash -

RUN apt-get update && apt install -y \
        nodejs

# install pyenv for managing python versions
RUN curl https://pyenv.run | bash

# install python
RUN /root/.pyenv/bin/pyenv install ${PYTHON_VERSION}
RUN /root/.pyenv/bin/pyenv global ${PYTHON_VERSION}
ENV PATH="/root/.pyenv/bin:/root/.pyenv/versions/${PYTHON_VERSION}/bin:$PATH"

RUN mkdir /newsgac
COPY requirements.jupyter.txt /newsgac/requirements.txt
RUN pip install -r /newsgac/requirements.txt

RUN python -m ipykernel install

RUN jupyter labextension install @jupyterlab/hub-extension
RUN jupyter nbextension enable --py widgetsnbextension
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager

WORKDIR /newsgac

COPY jupyter/jupyterhub_config.py /jupyterhub_config.py
COPY newsgac /newsgac/newsgac

COPY setup.py /newsgac/setup.py

RUN python setup.py install

RUN ["bash", "-c", "python <<< \"import nltk; nltk.download('punkt')\""]

COPY jupyter/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD jupyterhub -f /jupyterhub_config.py
