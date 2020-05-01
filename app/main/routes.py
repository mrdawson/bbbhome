from app import db
from app.main import bp
from flask import render_template
from flask_login import login_required, current_user
from app.models import User
import datetime


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        current_user.active = True
        db.session.commit()


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", title="Home Page")


@bp.route("/resume")
def resume():
    return render_template("resume.html", title="Resume")


@bp.route("/projects")
def projects():
    return render_template("projects.html", title="Projects")


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not user.last_seen:
        last_seen_str = f"{user.username} has never been seen..."
    elif datetime.datetime.utcnow() - user.last_seen < datetime.timedelta(seconds=20):
        last_seen_str = "Online"
    elif datetime.datetime.utcnow() - user.last_seen < datetime.timedelta(minutes=2):
        last_seen_str = "Last seen less than 2 minutes ago"
    else:
        last_seen_str = f"Last seen at {user.last_seen}UTC"
    return render_template("user.html", user=user, last_seen_str=last_seen_str)
