from models import AccountNotFound, AccountAlreadyExists, NicknameAlreadyExists
from flask import Flask, render_template, request, redirect, url_for, session, abort
from models import (get_games, get_game_info, add_user, get_user, search, get_user_lists, count_user_lists,
                    get_user_photo, add_to_list, delete_list, update_list_type, update_list_rating, get_user_list_type,
                    get_user_rating, get_game_genres, get_all_genres, get_all_developers, filter_games,
                    get_game_comments, add_comment)


def create_app():
    app = Flask(__name__)
    app.secret_key = 'KirokuPass'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        search_content = request.args.get('search-content')
        filter_year_from = request.args.get('year-from')
        filter_year_to = request.args.get('year-to')
        filter_genre = request.args.get('genre')
        filter_developer = request.args.get('developer')
        check_session(session)
        if search_content and search_content != '':
            searched_games = search(search_content)
            return render_template('index.html', games=searched_games, search=True, user=session['account'],
                                   user_photo=session['user_photo'])
        if filter_year_from or filter_year_to or filter_genre or filter_developer:
            all_games = filter_games(filter_year_from, filter_year_to, filter_genre, filter_developer)
        else:
            all_games = get_games()
        all_genres = get_all_genres()
        all_developers = get_all_developers()
        return render_template('index.html', games=all_games, user=session['account'], user_photo=session['user_photo'],
                               genres=all_genres, developers=all_developers)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['nickname']
            email = request.form['email']
            password = request.form['password']
            password_check = request.form['password_check']
            if password != password_check:
                return render_template('register.html', error='pass_not_match')
            try:
                add_user(name, email, password)
            except AccountAlreadyExists:
                return render_template('register.html', error='account_already_exists')
            return redirect('/login')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            try:
                user = get_user(email, password)
            except AccountNotFound:
                return render_template('login.html', account_not_found=True)
            session['account'] = user.Nickname
            return redirect('/users/' + session['account'])
        return render_template('login.html')

    @app.route('/users/<name>')
    def user_page(name):
        check_session(session)
        profile_photo = get_user_photo(name)
        user_lists = get_user_lists(name)
        list_counts = count_user_lists(name)
        return render_template('user.html', name=name, profile_photo=profile_photo, grouped_lists=user_lists,
                               list_counts=list_counts, user=session['account'], user_photo=session['user_photo'])

    @app.route('/game/<id_game>', methods=['GET', 'POST'])
    def game_page(id_game):
        if request.method == 'POST':
            comment_text = request.form['comment-text']
            add_comment(session['account'], id_game, comment_text)
            return redirect(url_for('game_page', id_game=id_game))
        check_session(session)
        game_data = get_game_info(id_game)
        list_type = get_user_list_type(session['account'], id_game)
        user_rating = get_user_rating(session['account'], id_game)
        genres = get_game_genres(id_game)
        comments = get_game_comments(id_game)
        return render_template('game.html', game_data=game_data, user=session['account'],
                               user_photo=session['user_photo'], list_type=list_type, user_rating=user_rating,
                               genres=genres, comments=comments)

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

    @app.route('/game/<id_game>/rating_update')
    def rating_handler(id_game):
        rating = request.args.get('rating')
        update_list_rating(session['account'], id_game, rating)
        return redirect(url_for('game_page', id_game=id_game))

    @app.route('/logout')
    def logout():
        session.pop('account', None)
        return redirect('/')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('not_found.html', user=session['account'], user_photo=session['user_photo']), 404

    def check_session(_session):
        if 'account' not in _session or _session['account'] is None:
            _session['account'] = None
            _session['user_photo'] = None
        else:
            _session['user_photo'] = get_user_photo(session['account'])

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
