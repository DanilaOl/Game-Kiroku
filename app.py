from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import get_games, get_game_info, add_user, get_user


def create_app():
    app = Flask(__name__)
    app.secret_key = 'KirokuPass'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        all_games = get_games()
        return render_template('index.html', games=all_games)

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
            session['account'] = name
            return redirect('/users/' + name)
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = get_user(email, password)
            session['account'] = user.Nickname
            return redirect('/users/' + user.Nickname)
        return render_template('login.html')

    @app.route('/users/<name>')
    def user_page(name):
        return render_template('user.html', name=name)

    @app.route('/game/<id_game>')
    def game_page(id_game):
        game = get_game_info(id_game)
        return render_template('game.html', game=game)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
