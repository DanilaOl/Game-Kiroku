import pytest
from models import get_user


# Определение наборов данных
@pytest.mark.parametrize(('nickname', 'email', 'password', 'password_check'),
                         [('TestUser1', 'test1@test.com', 'qwerty123456', 'qwerty123456'),
                          ('TestUser2', 'test2@test.com', 'loremipsum', 'loremipsum')])
# Тест функции регистрации
def test_registration(client, nickname, email, password, password_check):
    # Посылание POST-запроса с определёнными данными
    client.post('/register', data={'nickname': nickname, 'email': email,
                                   'password': password, 'password_check': password_check})
    # Запрос зарегистрированного пользователя из БД
    user = get_user(email, password)
    # Проверка соответствия данных из БД с исходными
    assert user.Nickname == nickname

