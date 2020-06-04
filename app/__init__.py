from flask import Flask
from config import Config
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from elasticsearch import Elasticsearch
from flask_mail import Mail
from flask_util_js import FlaskUtilJs
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import db, login

migrate = Migrate()
login.login_view = "auth.login"
mail = Mail()
fujs = FlaskUtilJs()
limiter = Limiter(key_func=get_remote_address,
                  default_limits=["200 per day", "50 per hour"])



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    fujs.init_app(app)
    limiter.init_app(app)

    app.elasticsearch = Elasticsearch([app.config["ELASTICSEARCH_URL"]]) if app.config[
        "ELASTICSEARCH_URL"] else None

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix="/projects")

    from app.homiechat import bp as homiechat_bp
    app.register_blueprint(homiechat_bp, url_prefix="/homiechat")

    from app.spellbook import bp as spellbook_bp
    app.register_blueprint(spellbook_bp, url_prefix="/spellbook")

    from app.library import bp as library_bp
    app.register_blueprint(library_bp, url_prefix="/library")

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=f"autobot@{app.config['MAIL_SERVER']}",
                toaddrs=app.config["ADMINS"], subject="carlsdawson.com Error",
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('/var/log/carlsdawson'):
            os.mkdir('/var/log/carlsdawson')
        file_handler = RotatingFileHandler('/var/log/carlsdawson/carlsdawson.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('CarlSDawson.com startup')

    return app


from . import models, errors
