from flask import url_for

from test.helpers import is_valid_html
from newsgac.data_sources.tasks import process


def test_get_data_source(app, client, data_source_balanced_100):
    client.login()
    data_source = data_source_balanced_100
    url = url_for('data_sources.view', data_source_id=data_source._id)
    sv = client.get(url)
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


def test_get_data_source_stats(client, data_source_balanced_100):
    client.login()
    data_source = data_source_balanced_100
    process(data_source._id)
    url = url_for('data_sources.view', data_source_id=data_source._id)
    sv = client.get(url)
    assert sv.status_code == 200
    assert is_valid_html(sv.data)


# def test_delete_data_source(client, data_source_balanced_100):
#     data_source = data_source_balanced_100
#     url = url_for('data_sources.get_data_source_page', data_source_id=data_source._id)
#     sv = client.get(url)
#     assert sv.status_code == 200
#     assert is_valid_html(sv.data)