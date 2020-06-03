from flask_mail import Message
from app import mail
from flask import current_app, render_template, send_from_directory
from threading import Thread
from app.helpers import get_book_file
import os
import glob
import mimetypes

mimetypes.init()
mimetypes.add_type("application/xhtml+xml", ".xhtml")
mimetypes.add_type("application/epub+zip", ".epub")
mimetypes.add_type("application/fb2+zip", ".fb2")
mimetypes.add_type("application/x-mobipocket-ebook", ".mobi")
mimetypes.add_type("application/x-mobipocket-ebook", ".prc")
mimetypes.add_type("application/vnd.amazon.ebook", ".azw")
mimetypes.add_type("application/octet-stream", ".azw3")
mimetypes.add_type("application/x-cbr", ".cbr")
mimetypes.add_type("application/x-cbz", ".cbz")
mimetypes.add_type("application/x-cbt", ".cbt")
mimetypes.add_type("image/vnd.djvu", ".djvu")
mimetypes.add_type("application/mpeg", ".mpeg")
mimetypes.add_type("application/mpeg", ".mp3")
mimetypes.add_type("application/mp4", ".m4a")
mimetypes.add_type("application/mp4", ".m4b")
mimetypes.add_type("application/ogg", ".ogg")
mimetypes.add_type("application/ogg", ".oga")


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, attachments=()):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    for fname, content_type, data in attachments:
        msg.attach(fname, content_type, data)
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()


def send_password_reset_email(user):
    print(f"sending from: {current_app.config['ADMINS'][0]}")
    token = user.get_reset_password_token()
    send_email(
        "[carlsdawson.com] Reset Password",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )


def send_book_email(book, fmt, email, user):
    fmt = fmt.lower()
    if not book:
        return False, "Book not found."
    calibre_path = os.path.join(current_app.config["CALIBRE_PATH"], book.path)
    book_fname = glob.glob(f"{calibre_path}*/*.{fmt}")[0].split(os.sep)[-1]
    if not os.path.isfile(os.path.join(calibre_path, book_fname)):
        return False, "File not found."
    file_size = os.path.getsize(os.path.join(calibre_path, book_fname))
    print(file_size)
    if "gmail.com" in email and file_size > 24.999e6:
        return False, "Sorry, gmail cannot receive attachments larger than 25MB."
    if file_size > 24.999e6:
        return False, "Sorry, I can't send attachments larger than 25MB."
    with open(os.path.join(calibre_path, book_fname), "rb") as f:

        attachment = f.read()
        print(type(attachment))
        if not attachment:
            return
        authors = [a.name for a in book.authors]
        print("sending")
        send_email(
            f"E-Book: {book.title}",
            sender=current_app.config["ADMINS"][1],
            recipients=[email],
            text_body=render_template(
                "email/send_book.txt", user=user, book=book, authors=authors
            ),
            html_body=render_template(
                "email/send_book.html", user=user, book=book, authors=authors
            ),
            attachments=[(book_fname, mimetypes.types_map[f".{fmt}"], attachment)],
        )
    return True, "Success"
