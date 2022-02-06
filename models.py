from sqlalchemy import (Column, Integer, Float, String, Boolean, Text, Date, ForeignKey, create_engine, MetaData, Table)
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
