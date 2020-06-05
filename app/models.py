from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from .helpers import get_book_cover
from .search import add_to_index, remove_from_index, query_index
from time import time
import jwt
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()

############################### SITE MODELS ####################################


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __bind_key__ = "site"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    roles = db.relationship("Role", secondary="user_roles")

    rooms = db.relationship("Room", secondary="user_rooms")

    rooms_owned = db.relationship("Room", backref="owner", lazy="dynamic")

    posts = db.relationship("Post", backref="author", lazy="dynamic")

    devices = db.relationship("Device", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def update_roles(self, roles):
        if len(roles) == 0:
            roles = "Pleb"
        elif "Pleb" in roles and len(roles) >= 1:
            roles.remove("Pleb")
        self.roles = [Role.query.filter_by(name=r).first() for r in roles]

    def add_device(self, name, email):
        self.devices.append(Device(name=name, email=email))

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"<User {self.username}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Role(db.Model):
    __tablename__ = "roles"
    __bind_key__ = "site"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)

    def __repr__(self):
        return f"<Role {self.name}>"

    def __str__(self):
        return f"{self.name}"


roles_table = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE")),
    db.Column("role_id", db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE")),
    info={"bind_key": "site"}
)


rooms_table = db.Table(
    "user_rooms",
    db.Column("user_id", db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE")),
    db.Column("room_id", db.Integer(), db.ForeignKey("rooms.id", ondelete="CASCADE")),
    info={"bind_key": "site"}
)


class Device(db.Model):
    __tablename__ = "devices"
    __bind_key__ = "site"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))

    def __repr__(self):
        return f"<Device {self.name}>"


class Post(db.Model):
    __tablename__ = "posts"
    __bind_key__ = "site"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    def __repr__(self):
        return f"<Post {self.body}>"


class Room(db.Model):
    __tablename__ = "rooms"
    __bind_key__ = "site"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    posts = db.relationship("Post", backref="room", lazy="dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))


# class Temperature(db.Model):
#     __tablename__ = "temperature"
#     __bind_key__ = "site"
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     volt = db.Column(db.Float)
#     temp = db.Columnn(db.Float)
#
#     def __repr__(self):
#         return f"<T = {self.temp}F"


############################### CALIBRE MODELS ####################################


class SearchableMixin:
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        print(ids, total)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)


class Identifiers(db.Model):
    __tablename__ = "identifiers"
    __bind_key__ = "calibre"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    val = db.Column(db.String)
    book = db.Column(db.Integer, db.ForeignKey("books.id"))

    def __init__(self, val, id_type, book):
        self.val = val
        self.type = id_type
        self.book = book

    def formatType(self):
        if self.type == "amazon":
            return "Amazon"
        elif self.type == "isbn":
            return "ISBN"
        elif self.type == "doi":
            return "DOI"
        elif self.type == "goodreads":
            return "Goodreads"
        elif self.type == "google":
            return "Google Books"
        elif self.type == "kobo":
            return "Kobo"
        if self.type == "lubimyczytac":
            return "Lubimyczytac"
        else:
            return self.type

    def __repr__(self):
        if self.type == "amazon":
            return "https://amzn.com/{0}".format(self.val)
        elif self.type == "isbn":
            return "http://www.worldcat.org/isbn/{0}".format(self.val)
        elif self.type == "doi":
            return "http://dx.doi.org/{0}".format(self.val)
        elif self.type == "goodreads":
            return "http://www.goodreads.com/book/show/{0}".format(self.val)
        elif self.type == "douban":
            return "https://book.douban.com/subject/{0}".format(self.val)
        elif self.type == "google":
            return "https://books.google.com/books?id={0}".format(self.val)
        elif self.type == "kobo":
            return "https://www.kobo.com/ebook/{0}".format(self.val)
        elif self.type == "lubimyczytac":
            return " http://lubimyczytac.pl/ksiazka/{0}".format(self.val)
        elif self.type == "url":
            return "{0}".format(self.val)
        else:
            return ""


class Comments(db.Model):
    __tablename__ = "comments"
    __bind_key__ = "calibre"
    __searchable__ = ["text"]

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    book = db.Column(db.Integer, db.ForeignKey("books.id"))

    def __init__(self, text, book):
        self.text = text
        self.book = book

    def __repr__(self):
        return "<Comments({0})>".format(self.text)


class Tags(db.Model):
    __tablename__ = "tags"
    __bind_key__ = "calibre"
    __searchable__ = ["name"]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tags('{0})>".format(self.name)


class Authors(db.Model):
    __tablename__ = "authors"
    __bind_key__ = "calibre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sort = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, name, sort, link):
        self.name = name
        self.sort = sort
        self.link = link

    def __repr__(self):
        return "<Authors('{0},{1}{2}')>".format(self.name, self.sort, self.link)


class Series(db.Model):
    __tablename__ = "series"
    __bind_key__ = "calibre"
    __searchable__ = ["name"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sort = db.Column(db.String)

    def __init__(self, name, sort):
        self.name = name
        self.sort = sort

    def __repr__(self):
        return "<Series('{0},{1}')>".format(self.name, self.sort)


class Ratings(db.Model):
    __tablename__ = "ratings"
    __bind_key__ = "calibre"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)

    def __init__(self, rating):
        self.rating = rating

    def __repr__(self):
        return "<Ratings('{0}')>".format(self.rating)


class Languages(db.Model):
    __tablename__ = "languages"
    __bind_key__ = "calibre"

    id = db.Column(db.Integer, primary_key=True)
    lang_code = db.Column(db.String)

    def __init__(self, lang_code):
        self.lang_code = lang_code

    def __repr__(self):
        return "<Languages('{0}')>".format(self.lang_code)


class Publishers(db.Model):
    __tablename__ = "publishers"
    __bind_key__ = "calibre"
    __searchable__ = ["name"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sort = db.Column(db.String)

    def __init__(self, name, sort):
        self.name = name
        self.sort = sort

    def __repr__(self):
        return "<Publishers('{0},{1}')>".format(self.name, self.sort)


class Data(db.Model):
    __tablename__ = "data"
    __bind_key__ = "calibre"

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, db.ForeignKey("books.id"))
    format = db.Column(db.String)
    uncompressed_size = db.Column(db.Integer)
    name = db.Column(db.String)

    def __init__(self, book, book_format, uncompressed_size, name):
        self.book = book
        self.format = book_format
        self.uncompressed_size = uncompressed_size
        self.name = name

    def __repr__(self):
        return "<Data('{0},{1}{2}{3}')>".format(
            self.book, self.format, self.uncompressed_size, self.name
        )


books_authors_link = db.Table(
    "books_authors_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("author", db.Integer, db.ForeignKey("authors.id"), primary_key=True),
    info={"bind_key": "calibre"}
)

books_tags_link = db.Table(
    "books_tags_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("tag", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
    info={"bind_key": "calibre"}
)

books_series_link = db.Table(
    "books_series_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("series", db.Integer, db.ForeignKey("series.id"), primary_key=True),
    info={"bind_key": "calibre"}
)

books_ratings_link = db.Table(
    "books_ratings_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("rating", db.Integer, db.ForeignKey("ratings.id"), primary_key=True),
    info={"bind_key": "calibre"}
)

books_languages_link = db.Table(
    "books_languages_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("lang_code", db.Integer, db.ForeignKey("languages.id"), primary_key=True),
    info={"bind_key": "calibre"}
)

books_publishers_link = db.Table(
    "books_publishers_link",
    db.Column("book", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column(
        "publisher", db.Integer, db.ForeignKey("publishers.id"), primary_key=True
    ),
    info={"bind_key": "calibre"}
)


class Book(SearchableMixin, db.Model):
    __tablename__ = "books"
    __bind_key__ = "calibre"
    __searchable__ = [
        "title",
        "author_sort",
        "tags.name",
        "series.name",
        "publishers.name",
        "comments.text",
    ]

    DEFAULT_PUBDATE = "0101-01-01 00:00:00+00:00"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    sort = db.Column(db.String)
    author_sort = db.Column(db.String)
    timestamp = db.Column(db.TIMESTAMP)
    pubdate = db.Column(db.String)
    series_index = db.Column(db.String)
    last_modified = db.Column(db.TIMESTAMP)
    path = db.Column(db.String)
    has_cover = db.Column(db.Integer)
    uuid = db.Column(db.String)

    authors = db.relationship("Authors", secondary=books_authors_link, backref="books")
    tags = db.relationship(
        "Tags", secondary=books_tags_link, backref="books", order_by="Tags.name"
    )
    comments = db.relationship("Comments", backref="books")
    data = db.relationship("Data", backref="books")
    series = db.relationship("Series", secondary=books_series_link, backref="books")
    ratings = db.relationship("Ratings", secondary=books_ratings_link, backref="books")
    languages = db.relationship(
        "Languages", secondary=books_languages_link, backref="books"
    )
    publishers = db.relationship(
        "Publishers", secondary=books_publishers_link, backref="books"
    )
    identifiers = db.relationship("Identifiers", backref="books")

    def __init__(
        self,
        title,
        sort,
        author_sort,
        timestamp,
        pubdate,
        series_index,
        last_modified,
        path,
        has_cover,
        authors,
        tags,
        languages=None,
    ):
        self.title = title
        self.sort = sort
        self.author_sort = author_sort
        self.timestamp = timestamp
        self.pubdate = pubdate
        self.series_index = series_index
        self.last_modified = last_modified
        self.path = path
        self.has_cover = has_cover

    def __repr__(self):
        return "<Books('{0},{1}{2}{3}{4}{5}{6}{7}{8}')>".format(
            self.title,
            self.sort,
            self.author_sort,
            self.timestamp,
            self.pubdate,
            self.series_index,
            self.last_modified,
            self.path,
            self.has_cover,
        )

    def get_formats(self):
        return [d.format for d in self.data]

    def get_cover(self):
        return get_book_cover(self, True)

    @property
    def atom_timestamp(self):
        return self.timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00") or ""
