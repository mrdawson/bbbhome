from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

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
                fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs=app.config["ADMINS"], subject="carlsdawson.com Error",
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.adHandler(mail_handler)
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/carlsdawson.log', maxBytes=10240,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('CarlSDawson.com startup')

    return app


from app import models, errors
