from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import get_games, get_game_info, add_user, get_user, search, get_user_lists, count_user_lists, get_user_photo
# TODO add filters and sorting
# TODO add contact info to footer
# TODO replace js menu with css:hover menu

# создание приложения с обработкой всех путей
def create_app():
    app = Flask(__name__)
    # задание секретного ключа для работы с cookie
    app.secret_key = 'KirokuPass'

    # обработка главной страницы
    @app.route('/', methods=['GET', 'POST'])
    def index():
        # получение запроса из поисковой строки
        search_content = request.args.get('search-content')
        # TODO move session['account'] stuff to separate function or think about using flask-login
        # проверка авторизации пользователя
        if 'account' not in session or session['account'] is None:
            session['account'] = None
            user_photo = None
        else:
            # TODO move user_photo to session['user_photo'] and think about naming
            user_photo = get_user_photo(session['account'])
        if search_content and search_content != '':
            # поиск по введённой фразе и выдача результатов на главную страницу
            searched_games = search(search_content)
            return render_template('index.html', games=searched_games, search=True, user=session['account'],
                                   user_photo=user_photo)
        # получение всех игр из БД
        all_games = get_games()
        # отрисовка необходимого html-файла с нужными параметрами
        return render_template('index.html', games=all_games, user=session['account'], user_photo=user_photo)

    # обработка страницы регистрации
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # если пользователь отпрафил форму регистрации
        if request.method == 'POST':
            # получение данных из полей формы
            name = request.form['nickname']
            email = request.form['email']
            password = request.form['password']
            password_check = request.form['password_check']
            if password != password_check:
                return render_template('register.html', error='pass_not_match')
            # добавление пользователя в БД
            add_user(name, email, password)
            # переадресация на страницу авторизации
            return redirect('/login')
        # если пользователь только зашёл на страницу
        return render_template('register.html')

    # обработка страницы авторизации
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # если пользователь отправил форму авторизации
        if request.method == 'POST':
            # получение данных из полей форм
            email = request.form['email']
            password = request.form['password']
            user = get_user(email, password)
            # добавление пользователя в текущую сессию
            session['account'] = user.Nickname
            # переадресация на страницу профиля пользователя
            return redirect('/users/' + session['account'])
        # если пользователь только зашёл на страницу
        return render_template('login.html')

    # обработка страницы профиля пользователя
    @app.route('/users/<name>')
    def user_page(name):
        # TODO add head to the lists' tables
        # проверка авторизации пользователя
        if 'account' not in session or session['account'] is None:
            session['account'] = None
            user_photo = None
        else:
            user_photo = get_user_photo(session['account'])
        # получение данных необходимых для отображения на странице
        profile_photo = get_user_photo(name)
        user_lists = get_user_lists(name)
        list_counts = count_user_lists(name)
        # отрисовка html-файла с необходимыми данными
        return render_template('user.html', name=name, profile_photo=profile_photo, grouped_lists=user_lists,
                               list_counts=list_counts, user=session['account'], user_photo=user_photo)

    # обработка страницы игры
    @app.route('/game/<id_game>')
    def game_page(id_game):
        # проверка авторизации пользователя
        if 'account' not in session or session['account'] is None:
            session['account'] = None
            user_photo = None
        else:
            user_photo = get_user_photo(session['account'])
        # получение данных необходимых для отображения на странице
        game_data = get_game_info(id_game)
        # отрисовка html-файла с необходимыми данными
        return render_template('game.html', game_data=game_data, user=session['account'], user_photo=user_photo)

    # обработка выхода пользователя из аккаунта
    @app.route('/logout')
    def logout():
        # удаление текущего пользователя из сессии
        session.pop('account', None)
        # переадресация на главную страницу
        return redirect('/')

    return app


# запуск приложения
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
