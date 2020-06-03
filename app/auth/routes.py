from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ManageUserForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.wrappers import roles_required
from app.models import User, Role
from flask_login import login_user, logout_user, current_user, login_required
from app.email import send_password_reset_email


@bp.route("/denied/<required_clearance>")
def denied(required_clearance):
    clearance = "-".join([c.strip("'(),") for c in required_clearance.split(",")][:-1])
    usr_clearance = "-".join([str(role) for role in current_user.roles])
    return render_template("/auth/denied.html", title="Access Denied", clearance=clearance, usr_clearance=usr_clearance)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        if not form.username.data:
            flash("enter a username")
            return redirect(url_for("auth.login"))
        if not form.password.data:
            flash("enter a password")
            return redirect(url_for("auth.login"))
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if not user:
            user = User.query.filter_by(email=form.username.data.lower()).first()
        if not user:
            flash(f"no account is registered with the username '{form.username.data.lower()}'")
            return redirect(url_for("auth.login"))
        if not user.check_password(form.password.data):
            flash("invalid username/password combination")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        pleb = Role.query.filter_by(name="Pleb").first()
        user.roles.append(pleb)
        db.session.add(user)
        db.session.commit()
        flash("Registration was Successful, Welcome.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/manage/<username>", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def manage_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_roles = [str(role) for role in user.roles]
    form = ManageUserForm()
    if not form.is_submitted():
        for role_field in [form.pleb, form.homie, form.wizard, form.scribe, form.admin]:
            if role_field.label.text in user_roles:
                role_field.data = True
    if form.validate_on_submit():
        new_user_roles = []
        for role_field in [form.pleb, form.homie, form.wizard, form.scribe, form.admin]:
            if role_field.data:
                new_user_roles.append(role_field.label.text)
        user.update_roles(new_user_roles)
        db.session.commit()
        flash("Changes applied successfully")
    return render_template("auth/manage.html", username=username, form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)