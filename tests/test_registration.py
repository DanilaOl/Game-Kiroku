import pytest
from models import get_user


@pytest.mark.parametrize(('nickname', 'email', 'password', 'password_check'),
                         [('TestUser1', 'test1@test.com', 'qwerty123456', 'qwerty123456'),
                          ('TestUser2', 'test2@test.com', 'loremipsum', 'loremipsum')])
def test_registration(client, nickname, email, password, password_check):
    client.post('/register', data={'nickname': nickname, 'email': email,
                                   'password': password, 'password_check': password_check})
    user = get_user(email, password)
    assert user.Nickname == nickname
