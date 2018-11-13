FROM jupyterhub/jupyterhub

RUN apt-get update && apt install -y build-essential

RUN mkdir /newsgac

COPY requirements.txt /newsgac/requirements.txt

RUN pip install jupyter jupyterlab && \
    conda create -n py27 python=2.7 && \
    /opt/conda/envs/py27/bin/pip install jupyter ipykernel setuptools wheel && \
    /opt/conda/envs/py27/bin/pip install -r /newsgac/requirements.txt && \
    /opt/conda/envs/py27/bin/python -m ipykernel install

RUN jupyter labextension install @jupyterlab/hub-extension


WORKDIR /newsgac

COPY jupyter/jupyterhub_config.py /jupyterhub_config.py
COPY newsgac /newsgac/newsgac

COPY setup.py /newsgac/setup.py

RUN /opt/conda/envs/py27/bin/python setup.py install

RUN /opt/conda/envs/py27/bin/python -m spacy download nl_core_news_sm
RUN ["bash", "-c", "/opt/conda/envs/py27/bin/python <<< \"import nltk; nltk.download('punkt')\""]

COPY jupyter/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD jupyterhub -f /jupyterhub_config.py
