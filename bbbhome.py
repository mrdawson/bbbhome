from app import create_app
from app.models import db, User, Role, Book

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Role": Role, "Book": Book}
