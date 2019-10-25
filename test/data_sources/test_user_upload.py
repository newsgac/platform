import pytest

from newsgac.data_sources.models import DataSource
from test.helpers import is_valid_html


@pytest.fixture(autouse=True)
def login(test_user, client):
    client.login()


def test_index_page(client):
    sv = client.get('/data_sources/')
    if not sv.status_code == 200: raise AssertionError()
    if not is_valid_html(sv.data): raise AssertionError()


def test_new_page(client):
    sv = client.get('/data_sources/new')
    if not sv.status_code == 200: raise AssertionError()
    if not is_valid_html(sv.data): raise AssertionError()


#@pytest.mark.timeout(10)
def test_upload(client, dataset_balanced_100):
    sv = client.post('/data_sources/new', data=dict(
        file=(dataset_balanced_100, 'dataset.txt'),
        display_title="Test data set",
        description="For testing purposes"
    ))
    if not sv.status_code == 302: raise AssertionError()


def test_upload_created_datasource():
    data_source = list(DataSource.objects.all())[0]
    if not data_source.display_title == "Test data set": raise AssertionError()
    if not len(data_source.articles) == 100: raise AssertionError()
