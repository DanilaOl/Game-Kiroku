from sqlalchemy import Column, Integer, Float, String, Boolean, Text, Date, ForeignKey, create_engine, MetaData, Table, func
from sqlalchemy.orm import relationship, Session, sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
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


def get_games():
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                           echo=True)
    session = Session(bind=engine)
    all_games = session.query(Game).all()
    session.close()
    return all_games


def get_game_info(id_game):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                           echo=True)
    session = Session(bind=engine)
    game = session.query(Game).get(id_game)
    return game


def add_user(name, email, password):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                           echo=True)
    session = Session(bind=engine)
    user = Users(Nickname=name, Email=email, Password=password)
    session.add(user)
    session.commit()
    session.close()


def get_user(email, password):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                           echo=True)
    session = Session(bind=engine)
    user = session.query(Users).filter_by(Email=email).first()
    session.close()
    if not user or (password != user.Password):
        raise AccountNotFound
    return user


def search(query):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                           echo=True)
    session = Session(bind=engine)
    searched_games = session.query(Game).filter(Game.Game_name.like(f"%{query}%")).all()
    session.close()
    return searched_games


def get_user_lists(name):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                          echo=True)
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    user_lists = {'planned': session.query(List).filter_by(ID_user=id_user).filter_by(List_type='planned').all(),
                  'completed': session.query(List).filter_by(ID_user=id_user).filter_by(List_type='completed').all(),
                  'dropped': session.query(List).filter_by(ID_user=id_user).filter_by(List_type='dropped').all(),
                  'postponed': session.query(List).filter_by(ID_user=id_user).filter_by(List_type='postponed').all()}
    return user_lists


def count_user_lists(name):
    engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                          echo=True)
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    counts = dict(session.query(List.List_type, func.count(List.ID_user)).filter_by(ID_user=id_user).group_by(List.List_type).all())
    if len(counts) != 4:
        if 'planned' not in counts:
            counts['planned'] = 0
        if 'completed' not in counts:
            counts['completed'] = 0
        if 'dropped' not in counts:
            counts['dropped'] = 0
        if 'postponed' not in counts:
            counts['postponed'] = 0
    return counts
