from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120, collation="utf8mb4_unicode_ci"), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    roles = db.relationship("Role", secondary="user_roles")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"<Role {self.name}>"

    def __str__(self):
        return f"{self.name}"


class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<UID {self.user_id}, RID {self.role_id}>"
