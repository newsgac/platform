from test.helpers import is_valid_html


def test_get_root(client):
    data = client.get('/').data.decode('utf-8')
    assert 'NEWSGAC' in data
    assert is_valid_html(data)
