from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import (get_games, get_game_info, add_user, get_user, search, get_user_lists, count_user_lists,
                    get_user_photo, add_to_list, delete_list, update_list_type, update_list_rating, get_user_list_type)
# TODO add filters and sorting
# TODO add contact info to footer
# TODO replace js menu with css:hover menu


def create_app():
    app = Flask(__name__)
    app.secret_key = 'KirokuPass'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        search_content = request.args.get('search-content')
        check_session(session)
        if search_content and search_content != '':
            searched_games = search(search_content)
            return render_template('index.html', games=searched_games, search=True, user=session['account'],
                                   user_photo=session['user_photo'])
        all_games = get_games()
        return render_template('index.html', games=all_games, user=session['account'], user_photo=session['user_photo'])

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
        # TODO add head to the lists' tables
        check_session(session)
        profile_photo = get_user_photo(name)
        user_lists = get_user_lists(name)
        list_counts = count_user_lists(name)
        return render_template('user.html', name=name, profile_photo=profile_photo, grouped_lists=user_lists,
                               list_counts=list_counts, user=session['account'], user_photo=session['user_photo'])

    @app.route('/game/<id_game>')
    def game_page(id_game):
        check_session(session)
        game_data = get_game_info(id_game)
        list_type = get_user_list_type(session['account'], id_game)
        return render_template('game.html', game_data=game_data, user=session['account'],
                               user_photo=session['user_photo'], list_type=list_type)

    @app.route('/game/<id_game>/list_update')
    def list_handler(id_game):
        list_type = request.args.get('type')
        if list_type == 'delete':
            delete_list(session['account'], id_game)
        else:
            if get_user_list_type(session['account'], id_game):
                update_list_type(session['account'], id_game, list_type)
            else:
                add_to_list(session['account'], id_game, list_type)
        return redirect(url_for('game_page', id_game=id_game))

    @app.route('/logout')
    def logout():
        session.pop('account', None)
        return redirect('/')

    def check_session(_session):
        if 'account' not in session or session['account'] is None:
            _session['account'] = None
            _session['user_photo'] = None
        else:
            _session['user_photo'] = get_user_photo(session['account'])

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
