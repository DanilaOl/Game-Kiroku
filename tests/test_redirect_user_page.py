import pytest


# Определение наборов данных
@pytest.mark.parametrize(('name', 'exists'), [('TestUser', True), ('TestUserNE', False)])
# Тест функции перехода на страницы пользователя
def test_redirect_user_page(client, name, exists):
    # Если предполагается, что пользователь существует
    if exists:
        # Код состояния ответа сервера должен быть 200
        assert client.get(f'/users/{name}').status_code == 200
    # Если предполагается, что пользователь не существует
    else:
        # Код состояния ответа сервера должен быть 404
        assert client.get(f'/users/{name}').status_code == 404

