FROM jupyterhub/jupyterhub

RUN apt-get update && apt install -y build-essential

RUN mkdir /newsgac

COPY requirements.txt /newsgac/requirements.txt

RUN pip install jupyter && \
    conda create -n py27 python=2.7 && \
    /opt/conda/envs/py27/bin/pip install jupyter ipykernel setuptools wheel && \
    /opt/conda/envs/py27/bin/pip install -r /newsgac/requirements.txt && \
    /opt/conda/envs/py27/bin/python -m ipykernel install

WORKDIR /newsgac

COPY jupyter/jupyterhub_config.py /jupyterhub_config.py
COPY newsgac /newsgac/newsgac

COPY setup.py /newsgac/setup.py

RUN /opt/conda/envs/py27/bin/python setup.py install

COPY jupyter/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD jupyterhub -f /jupyterhub_config.py