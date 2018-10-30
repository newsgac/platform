FROM python:2.7

MAINTAINER abilgin

RUN groupadd -g 999 flask && \
    useradd -r -u 999 -g flask flask

RUN mkdir /newsgac

COPY requirements.txt /newsgac/requirements.txt
RUN pip install -r /newsgac/requirements.txt

COPY entrypoint.sh /newsgac
RUN chmod a+x /newsgac/entrypoint.sh
COPY newsgac /newsgac/newsgac

RUN ["bash", "-c", "python <<< \"import nltk; nltk.download('punkt')\""]

WORKDIR /newsgac

COPY test /newsgac/test

ENTRYPOINT ["/newsgac/entrypoint.sh"]

CMD ["echo", "You should define a command in docker-compose.yml"]
