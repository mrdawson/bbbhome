from app.library import bp
from flask import render_template, request, redirect, url_for, make_response
from app.helpers import get_book_cover
from app.models import Book, Device
from app.library.forms import SearchForm, NewDeviceForm
from flask import g, current_app, flash, jsonify
from flask_login import current_user, login_required
from app.auth.wrappers import roles_required
from app import db
from datetime import datetime
from app.email import send_book_email
from app.helpers import get_book_file
from app import limiter

sort_options = [
    ("title_asc", "Title ↑"),
    ("title_desc", "Title ↓"),
    ("author_asc", "Author ↑"),
    ("author_desc", "Author ↓"),
    ("added_asc", "Date Added ↑"),
    ("added_desc", "Date Added ↓"),
]


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.search_form = SearchForm()


@bp.route("/")
@bp.route("/index")
@login_required
@roles_required("Scribe")
def index():
    books = Book.query.order_by(Book.timestamp.desc()).limit(10).all()
    return render_template("library.html", title="Home Page", books=books)


@bp.route("/search")
@login_required
@roles_required("Scribe")
def search():
    if not g.search_form.validate():
        return redirect(url_for("library.stacks"))
    page = request.args.get("page", 1, type=int)
    books, total = Book.search(
        g.search_form.q.data, page, current_app.config["BOOKS_PER_PAGE"]
    )
    next_url = (
        url_for("library.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["BOOKS_PER_PAGE"]
        else None
    )
    return render_template(
        "/library/search.html",
        title="Search",
        books=books,
        sort_options=sort_options,
        next_url=next_url,
    )


@bp.route("/stacks")
@login_required
@roles_required("Scribe")
def stacks():
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "author_asc", type=str)

    if sort == "author_asc":
        books = Book.query.order_by(Book.author_sort.asc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    elif sort == "author_desc":
        books = Book.query.order_by(Book.author_sort.desc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    elif sort == "title_asc":
        books = Book.query.order_by(Book.sort.asc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    elif sort == "title_desc":
        books = Book.query.order_by(Book.sort.desc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    elif sort == "added_asc":
        books = Book.query.order_by(Book.timestamp.asc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    elif sort == "added_desc":
        books = Book.query.order_by(Book.timestamp.desc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
    else:
        books = Book.query.order_by(Book.timestamp.desc()).paginate(
            page, current_app.config["BOOKS_PER_PAGE"], False
        )
        sort = "added_desc"

    return render_template(
        "/library/stacks.html",
        title="Library",
        books=books.items,
        sort=sort,
        sort_options=sort_options
    )

@bp.route("/stacks/<int:book_id>")
@login_required
@roles_required("Scribe")
def book_info(book_id):
    book = Book.query.filter_by(id=book_id).first_or_404()
    return render_template("/library/book_info.html", book=book)


@bp.route("/sent")
@login_required
@roles_required("Scribe")
def sent(format, email):
    return render_template("/library/sent.html", )


@bp.route("/send_book", methods=["POST"])
@login_required
@roles_required("Scribe")
def send_book():
    book_id = request.form["book_id"]
    email = request.form["email"]
    format = request.form["format"]
    book = Book.query.filter_by(id=book_id).first()
    if format not in [d.format for d in book.data]:
        return jsonify({"success": False})
    valid_emails = [dev.email for dev in current_user.devices]
    valid_emails.append(current_user.email)
    if email not in valid_emails:
        return jsonify({"success": False})

    success, msg = send_book_email(book, format, email, current_user)
    return jsonify({"success": success, "msg": msg})


@bp.route("/download_book/<int:book_id>/<fmt>")
@login_required
@roles_required("Scribe")
@limiter.limit("1 per minute")
def download_book(book_id, fmt):
    book = Book.query.filter_by(id=book_id).first()
    return get_book_file(book, fmt, as_attachment=True)


@bp.route("/cover/<int:book_id>")
@login_required
@roles_required("Scribe")
def get_cover(book_id):
    book = Book.query.filter_by(id=book_id).first_or_404()
    return get_book_cover(book, True)


@bp.route("/manage_devices")
@login_required
@roles_required("Scribe")
def manage_devices():
    return render_template("/library/manage_devices.html")


@bp.route("/manage_devices/new_device", methods=["GET", "POST"])
@login_required
@roles_required("Scribe")
def new_device():
    form = NewDeviceForm()
    if form.validate_on_submit():
        dev = Device(name=form.name.data, email=form.email.data, user_id=current_user.id)
        db.session.add(dev)
        db.session.commit()
        flash("New Device Added")
        return redirect(url_for("library.manage_devices"))

    return render_template("/library/new_device.html", title="New Device", form=form)


@bp.route("/manage_devices/remove_device", methods=["POST"])
@login_required
@roles_required("Scribe")
def remove_device():
    dev = Device.query.filter_by(id=request.form["device_id"]).first_or_404()
    response = {"removed": {"id": dev.id, "email": dev.email, "name": dev.name}}
    db.session.delete(dev)
    db.session.commit()
    return jsonify(response)
