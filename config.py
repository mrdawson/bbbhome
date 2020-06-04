import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "default.db")
    SITE_DATABASE_URI = os.environ.get(
        "SITE_DATABASE_URI"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    CALIBRE_DATABASE_URI = os.environ.get(
        "CALIBRE_DATABASE_URI"
    ) or "sqlite:///" + os.path.join(basedir, "metadata.db")
    SQLALCHEMY_BINDS = {
        'site': SITE_DATABASE_URI,
        'calibre': CALIBRE_DATABASE_URI
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = datetime.timedelta(hours=1)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["autobot@carlsdawson.com", "library@carlsdawson.com", "admin@carlsdawson.com"]
    PLATFORM = os.environ.get("PLATFORM")
    CALIBRE_PATH = os.environ.get("CALIBRE_PATH")
    ELASTICSEARCH_URL = "http://localhost:9200"
    BOOKS_PER_PAGE = 20
