from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from werkzeug.security import generate_password_hash, check_password_hash


# подключение к базе данных
engine = create_engine('mssql+pyodbc://DESKTOP-4NS1C62\SQLEXPRESS/KirokuDB?driver=ODBC+Driver+17+for+SQL+Server',
                       echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

# назначение сущностей определённым классам
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
    # создание сессии, в рамках которой будет происходить обращение к БД
    session = Session(bind=engine)
    # запрос на получение записей обо всех играх
    all_games = session.query(Game).all()
    # закрытие сессии
    session.close()
    return all_games


def get_game_info(id_game):
    session = Session(bind=engine)
    # запрос на получение записи об игре вместе с информацией о разработчике и издателе
    game = (session.query(Game, Developer, Publisher)
            .outerjoin(Developer)
            .outerjoin(Publisher)
            .filter(Game.ID_game == id_game)
            .first())
    session.close()
    return game


def add_user(name, email, password):
    session = Session(bind=engine)
    # создание экземпляра класса User с введёнными параметрами
    user = Users(Nickname=name, Email=email, Password=password)
    # добавление пользователя в БД
    session.add(user)
    session.commit()
    session.close()


def get_user(email, password):
    session = Session(bind=engine)
    # запрос на получение записи о пользователе
    user = session.query(Users).filter_by(Email=email).first()
    session.close()
    # сравнение введённого пароля с имеющимся в БД
    if not user or (password != user.Password):
        raise AccountNotFound
    return user


def search(query):
    session = Session(bind=engine)
    # запрос на получение всех игр, удовлетворяющих поиску
    searched_games = (session.query(Game)
                      .filter(Game.Game_name.like(f"%{query}%"))
                      .all())
    session.close()
    return searched_games


def get_user_lists(name):
    session = Session(bind=engine)
    # получение ID пользователя по его имени
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user  # move this to separate func
    # первая часть запроса на получение списков пользователя
    q = (session.query(List, Game)
         .join(Game, List.ID_game == Game.ID_game)
         .filter(List.ID_user == id_user))
    # вторая часть запроса на получение списков пользователя и их распределение по категории
    user_lists = {'planned': q.filter(List.List_type == 'planned').all(),
                  'completed': q.filter(List.List_type == 'completed').all(),
                  'dropped': q.filter(List.List_type == 'dropped').all(),
                  'postponed': q.filter(List.List_type == 'postponed').all()}
    return user_lists


def count_user_lists(name):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    # подсчёт количества различных списков у пользователя
    counts = dict(session.query(List.List_type, func.count(List.ID_user))
                  .filter_by(ID_user=id_user)
                  .group_by(List.List_type)
                  .all())
    session.close()
    # присваивание нуля категории при отсутствии игры в списке
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


def get_user_photo(username):
    session = Session(bind=engine)
    # получение пути к фотографии пользователя
    photo = session.query(Users).filter_by(Nickname=name).first().Photo
    session.close()
    # если пользователь не добавлял фотографию, то используется стандартная
    if photo is None:
        return '../static/user_images/default.png'
    return photo


def add_to_list(name, id_game, category):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    user_list = List(ID_user=id_user, ID_game=id_game, List_type=category)
    session.add(user_list)
    session.commit()
    session.close()


def remove_from_list(name, id_game):
    session = Session(bind=engine)
    id_user = session.query(Users).filter_by(Nickname=name).first().ID_user
    session.query(List).filter(List.ID_user == id_user, List.ID_game == id_game).delete()
    session.commit()
    session.close()
