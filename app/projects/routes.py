from app.projects import bp
from flask import render_template


@bp.route("/mac1700")
def mac1700():
    return render_template("projects/mac1700.html", title="MAC1700 Restoration")


@bp.route("/klh20")
def klh20():
    return render_template("projects/klh20.html", title="KLH Model 20 Restoration")


@bp.route("/m2")
def m2():
    return render_template("projects/m2.html", title="M2 Clone")