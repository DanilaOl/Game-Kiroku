from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import get_games, add_user


app = Flask(__name__)
app.secret_key = 'kirokupass'


@app.route('/', methods=['GET', 'POST'])
def index():
    all_games = get_games()
    return render_template('index.html', games=all_games)

# @app.route('/games/<game_id>')
# def game_page(game_id):
#     games = get_games()


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


@app.route('/users/<name>')
def user_page(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)
