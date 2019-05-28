from newsgac.caches import Cache
from newsgac.common.utils import split_long_sentences, hash_text
from nltk import sent_tokenize
from pynlpl.clients.frogclient import FrogClient

from newsgac import config
from newsgac.tasks.celery_app import celery_app
from celery.signals import worker_init

worker_name=None


@worker_init.connect()
def setup_worker_name(sender, signal, **kwargs):
    global worker_name
    worker_name = sender.hostname


# @celery_app.task(base=ResultTask)
@celery_app.task()
def frog_process(texts):
    frogclient = FrogClient(
        config.frog_hostname,
        config.frog_port,
        returnall=True,
        timeout=1800.0,
    )
    for text in texts:
        cache = Cache.get_or_new(hash_text(text))
        sentences = [s for s in sent_tokenize(text) if s]
        sentences = split_long_sentences(sentences, 250)
        tokens = frogclient.process(' '.join(sentences))
        tokens_no_none = [token for token in tokens if None not in token]
        cache.data = tokens_no_none
        cache.save()
    frogclient.socket.close()
