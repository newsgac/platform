import pytest
from pymodm.errors import ValidationError

from newsgac.data_sources.models import DataSource
from test.helpers import is_valid_html


@pytest.fixture(autouse=True)
def login(client):
    client.login()


def test_index_page(client):
    sv = client.get('/data_sources/')
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


def test_new_page(client):
    sv = client.get('/data_sources/new')
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


def test_upload(client):
    import sys
    import os
    file_handler = open(os.path.join(sys.path[0], 'test', 'mocks', 'balanced_label_date_100.txt'), 'r')
    sv = client.post('/data_sources/new', data=dict(
        file=(file_handler, 'dataset.txt'),
        display_title="Test data set",
        description="For testing purposes"
    ))
    assert 1==2