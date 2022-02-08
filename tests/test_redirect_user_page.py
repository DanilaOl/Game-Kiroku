import pytest


@pytest.mark.parametrize(('name', 'exists'),
                         [('TestUser', True),
                          ('TestUserNE', False)])
def test_redirect_user_page(client, name, exists):
    if exists:
        assert client.get(f'/users/{name}').status_code == 200
    else:
        assert client.get(f'/users/{name}').status_code == 404
