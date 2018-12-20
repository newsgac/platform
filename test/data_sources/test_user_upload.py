import pytest

from newsgac.data_sources.models import DataSource
from test.helpers import is_valid_html


@pytest.fixture(autouse=True)
def login(test_user, client):
    client.login()


def test_index_page(client):
    sv = client.get('/data_sources/')
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


def test_new_page(client):
    sv = client.get('/data_sources/new')
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


#@pytest.mark.timeout(10)
def test_upload(client, dataset_balanced_100):
    sv = client.post('/data_sources/new', data=dict(
        file=(dataset_balanced_100, 'dataset.txt'),
        display_title="Test data set",
        description="For testing purposes"
    ))
    assert sv.status_code == 302


def test_upload_created_datasource():
    data_source = list(DataSource.objects.all())[0]
    assert data_source.display_title == "Test data set"
    assert len(data_source.articles) == 100
