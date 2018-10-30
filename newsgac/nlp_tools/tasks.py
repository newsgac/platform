import hashlib

from newsgac.caches import Cache
from newsgac.common.utils import split_long_sentences
from nltk import sent_tokenize
from pynlpl.clients.frogclient import FrogClient

from newsgac import config
from newsgac.tasks.celery_app import celery_app, ResultTask
from celery.signals import worker_init, worker_process_init

frogclient = None

worker_name=None

@worker_init.connect()
def setup_worker_name(sender, signal, **kwargs):
    global worker_name
    worker_name = sender.hostname


@worker_process_init.connect()
def setup_frog_conn(sender, signal, **kwargs):
    if worker_name.startswith('frog'):
        global frogclient
        frogclient = FrogClient(config.frog_hostname, config.frog_port, returnall=True)


@celery_app.task(base=ResultTask)
def frog_process(text):
    global frogclient
    cache = Cache.get_or_new(hashlib.sha1(text.encode('utf-8')).hexdigest())
    if not cache.data:
        sentences = [s for s in sent_tokenize(text) if s]
        sentences = split_long_sentences(sentences, 250)
        tokens = frogclient.process(' '.join(sentences))
        cache.data = [token for token in tokens if None not in token]
        cache.save()

    return cache.data
