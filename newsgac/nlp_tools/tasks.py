import hashlib

from newsgac.caches import Cache
from newsgac.common.utils import split_long_sentences
from nltk import sent_tokenize
from pynlpl.clients.frogclient import FrogClient

from newsgac import config
from newsgac.tasks.celery_app import celery_app, ResultTask
from celery.signals import worker_init

worker_name=None


@worker_init.connect()
def setup_worker_name(sender, signal, **kwargs):
    global worker_name
    worker_name = sender.hostname


@celery_app.task(base=ResultTask)
def frog_process(text):
    cache = Cache.get_or_new(hashlib.sha1(text.encode('utf-8')).hexdigest())
    if cache.data is None:
        frogclient = FrogClient(
            config.frog_hostname,
            config.frog_port,
            returnall=True,
            timeout=1800.0,
        )
        sentences = [s for s in sent_tokenize(text) if s]
        sentences = split_long_sentences(sentences, 250)
        tokens = frogclient.process(' '.join(sentences))
        cache.data = [token for token in tokens if None not in token]
        cache.save()
        frogclient.socket.close()
    return cache.data.get()
