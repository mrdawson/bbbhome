from app.homiechat import bp
from flask import render_template, url_for, redirect
from flask_login import login_required, current_user
from app.auth.wrappers import roles_required
from app.models import Post
from app.homiechat.forms import PostForm
from app import db


@bp.route("/chat", methods=["GET", "POST"])
@login_required
@roles_required("Homie")
def chat():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.dession.add(post)
        db.session.commit()
        return redirect(url_for("homiechat.chat"))
    return render_template("/homiechat/chat.html", title="Homie Chat")


@bp.route("/homies")
@login_required
@roles_required("Homie")
def homies():
    return render_template("/homiechat/homies.html", title="Homies")
