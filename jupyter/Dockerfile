FROM jupyterhub/jupyterhub

RUN apt-get update && apt install -y build-essential libmariadb-dev-compat

RUN mkdir /newsgac

COPY requirements.txt /newsgac/requirements.txt

RUN pip install jupyter jupyterlab && \
    conda create -n py310 python=3.10 && \
    /opt/conda/envs/py310/bin/pip install jupyter ipykernel setuptools wheel ipywidgets && \
    /opt/conda/envs/py310/bin/pip install -r /newsgac/requirements.txt && \
    /opt/conda/envs/py310/bin/python -m ipykernel install

RUN jupyter labextension install @jupyterlab/hub-extension
RUN jupyter nbextension enable --py widgetsnbextension
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager


WORKDIR /newsgac

COPY jupyter/jupyterhub_config.py /jupyterhub_config.py
COPY newsgac /newsgac/newsgac

COPY setup.py /newsgac/setup.py

RUN /opt/conda/envs/py310/bin/python setup.py install

#RUN /opt/conda/envs/py310/bin/python -m spacy download nl_core_news_sm
RUN ["bash", "-c", "/opt/conda/envs/py310/bin/python <<< \"import nltk; nltk.download('punkt')\""]

COPY jupyter/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD jupyterhub -f /jupyterhub_config.py
