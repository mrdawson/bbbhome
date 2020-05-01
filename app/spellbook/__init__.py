from flask import Blueprint

bp = Blueprint("spellbook", __name__)

from app.spellbook import routes