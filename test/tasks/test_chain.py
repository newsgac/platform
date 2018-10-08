from newsgac.tasks.tasks import sleep
from celery import chain
import pytest

@pytest.mark.skip()
def test_chain():
    res = chain(sleep.s(10), sleep.s(4), sleep.s(4))()
