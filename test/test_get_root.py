from test.helpers import is_valid_html


def test_get_root(client):
    data = client.get('/').data
    assert 'NEWSGAC' in data
    assert is_valid_html(data)
