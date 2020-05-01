from flask import Blueprint

bp = Blueprint("homiechat", __name__)

from app.homiechat import routes