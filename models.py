from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from werkzeug.security import generate_password_hash, check_password_hash


engine = create_engine(r'mssql+pyodbc://DESKTOP-16CHAPR\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                       echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

Developer = Base.classes.Developer
Game = Base.classes.Game
Genre = Base.classes.Genre
List = Base.classes.List
Publisher = Base.classes.Publisher
Users = Base.classes.Users


class AccountNotFound(Exception):
    """
    Account not found in database
    """


class AccountAlreadyExists(Exception):
    """
    Account is already in database
    """


class NicknameAlreadyExists(Exception):
    """
    Nickname is already in database
    """


def get_games():
    session = Session(bind=engine)
    all_games = session.query(Game).all()
    session.close()
    return all_games


def get_game_info(id_game):
    session = Session(bind=engine)
    game = (session.query(Game, Developer, Publisher)
            .outerjoin(Developer)
            .outerjoin(Publisher)
            .filter(Game.ID_game == id_game)
            .first())
    session.close()
    return game


def add_user(name, email, password):
    session = Session(bind=engine)
    user = Users(Nickname=name, Email=email, Password=password)
    try:
        session.add(user)
        session.commit()
        session.close()
    except IntegrityError:
        raise AccountAlreadyExists


def get_user(email, password):
    session = Session(bind=engine)
    user = session.query(Users).filter_by(Email=email).first()
    session.close()
    if not user or (password != user.Password):
        raise AccountNotFound
    return user


def search(query):
    session = Session(bind=engine)
    searched_games = (session.query(Game)
                      .filter(Game.Game_name.like(f"%{query}%"))
                      .all())
    session.close()
    return searched_games


def get_user_lists(name):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    q = (session.query(List, Game)
         .join(Game, List.ID_game == Game.ID_game)
         .filter(List.ID_user == id_user))
    user_lists = {'planned': q.filter(List.List_type == 'planned').all(),
                  'playing': q.filter(List.List_type == 'playing').all(),
                  'completed': q.filter(List.List_type == 'completed').all(),
                  'postponed': q.filter(List.List_type == 'postponed').all()}
    return user_lists


def count_user_lists(name):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    counts = dict(session.query(List.List_type, func.count(List.ID_user))
                  .filter_by(ID_user=id_user)
                  .group_by(List.List_type)
                  .all())
    session.close()
    if len(counts) != 4:
        if 'planned' not in counts:
            counts['planned'] = 0
        if 'playing' not in counts:
            counts['playing'] = 0
        if 'completed' not in counts:
            counts['completed'] = 0
        if 'postponed' not in counts:
            counts['postponed'] = 0
    return counts


def get_user_photo(username):
    session = Session(bind=engine)
    photo = session.query(Users).filter_by(Nickname=username).first().Photo
    session.close()
    if photo is None:
        return '../static/user_images/default.png'
    return photo


def add_to_list(name, id_game, list_type):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    user_list = List(ID_user=id_user, ID_game=id_game, List_type=list_type)
    session.add(user_list)
    session.commit()
    session.close()


def delete_list(name, id_game):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    session.query(List).filter(List.ID_user == id_user, List.ID_game == id_game).delete()
    session.commit()
    session.close()
    update_game_rating(id_game)


def update_list_type(name, id_game, list_type):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    (session.query(List)
     .filter(List.ID_user == id_user, List.ID_game == id_game)
     .update({'List_type': list_type}, synchronize_session="fetch"))
    session.commit()
    session.close()
    update_game_rating(id_game)


def update_list_rating(name, id_game, rating):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    (session.query(List)
     .filter(List.ID_user == id_user, List.ID_game == id_game)
     .update({'Rated': rating}, synchronize_session="fetch"))
    session.commit()
    session.close()
    update_game_rating(id_game)


def update_game_rating(id_game):
    session = Session(bind=engine)
    new_rating = (session.query(func.avg(List.Rated).label('avg_rating'))
                  .filter(List.ID_game == id_game)
                  .first()
                  .avg_rating)
    if new_rating is None:
        new_rating = 0
    (session.query(Game)
     .filter(Game.ID_game == id_game)
     .update({'Rating': new_rating}, synchronize_session="fetch"))
    session.commit()
    session.close()


def get_user_list_type(name, id_game):
    result = None
    if name is not None:
        session = Session(bind=engine)
        id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
        result = session.query(List).filter(List.ID_user == id_user, List.ID_game == id_game).first()
        session.close()
    if result:
        return result.List_type
    else:
        return None


def get_user_rating(name, id_game):
    result = None
    if name is not None:
        session = Session(bind=engine)
        id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
        result = session.query(List).filter(List.ID_user == id_user, List.ID_game == id_game).first()
        session.close()
    if result:
        return result.Rated
    else:
        return None
