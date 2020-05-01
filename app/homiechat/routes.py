from app.homiechat import bp
from flask import render_template
from flask_login import login_required
from app.auth.wrappers import roles_required


@bp.route("/chat")
@login_required
@roles_required("Homie")
def chat():
    return render_template("/homiechat/chat.html", title="Homie Chat")


@bp.route("/homies")
@login_required
@roles_required("Homie")
def homies():
    return render_template("/homiechat/homies.html", title="Homies")
