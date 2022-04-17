from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import get_games, get_game_info, add_user, get_user, search, get_user_lists, count_user_lists


def create_app():
    app = Flask(__name__)
    app.secret_key = 'KirokuPass'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        search_content = request.args.get('search-content')
        if 'account' not in session:
            session['account'] = None
        if search_content and search_content != '':
            searched_games = search(search_content)
            return render_template('index.html', games=searched_games, search=True, user=session['account'])
        else:
            all_games = get_games()
            return render_template('index.html', games=all_games, user=session['account'])

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['nickname']
            email = request.form['email']
            password = request.form['password']
            password_check = request.form['password_check']
            if password != password_check:
                return render_template('register.html', error='pass_not_match')
            add_user(name, email, password)
            return redirect('/login')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = get_user(email, password)
            session['account'] = user.Nickname
            return redirect('/users/' + session['account'])
        return render_template('login.html')

    @app.route('/users/<name>')
    def user_page(name):
        if 'account' not in session:
            session['account'] = None
        user_lists = get_user_lists(name)
        list_counts = count_user_lists(name)
        return render_template('user.html', name=name, lists=user_lists, list_counts=list_counts, user=session['account'])

    @app.route('/game/<id_game>')
    def game_page(id_game):
        if 'account' not in session:
            session['account'] = None
        game = get_game_info(id_game)
        return render_template('game.html', game=game, user=session['account'])

    @app.route('/logout')
    def logout():
        session.pop('account', None)
        return redirect('/')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
