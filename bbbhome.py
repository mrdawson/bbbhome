from app import create_app
from app.models import db, User, Role, Book
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Role": Role, "Book": Book}
