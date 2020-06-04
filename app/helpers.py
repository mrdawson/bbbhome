from flask import send_from_directory, current_app, safe_join, Response
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


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")


def get_cover_on_failure(use_generic_cover):
    if use_generic_cover:
        return send_from_directory(safe_join(STATIC_DIR, "images"), "generic_cover.jpg")
    else:
        return None


def get_book_cover(book, use_generic_cover_on_failure):
    if book and book.has_cover:
        try:
            calibre_path = os.path.join(os.environ.get("CALIBRE_PATH"), book.path)
            if os.path.isfile(os.path.join(calibre_path, "cover.jpg")):
                return send_from_directory(calibre_path, "cover.jpg")
            else:
                return get_cover_on_failure(use_generic_cover_on_failure)
        except EnvironmentError:
            return get_cover_on_failure(use_generic_cover_on_failure)
    else:
        return get_cover_on_failure(use_generic_cover_on_failure)


def get_book_file(book, fmt, as_attachment=True):
    if book:
        if True:
            calibre_path = os.path.join(current_app.config["CALIBRE_PATH"], book.path)
            book_fname = f"{book.data[0].name}.{fmt.lower()}"
            if os.path.isfile(os.path.join(calibre_path, book_fname)):
                print(f"found '{calibre_path}{os.sep}{book_fname}'")
                return send_from_directory(calibre_path, book_fname,
                                           mimetype=mimetypes.types_map[f".{fmt.lower()}"],
                                           as_attachment=as_attachment)
        try:
            x = 1
        except:
            return
    else:
        return


def get_book_filename(book, fmt):
    if book:
        try:
            calibre_path = os.path.join(current_app.config["CALIBRE_PATH"], book.path)
            book_fname = glob.glob(f"{calibre_path}*/*.{fmt}")[0].split(os.sep)[-1]
            if os.path.isfile(os.path.join(calibre_path, book_fname)):
                return book_fname
        except:
            return
    else:
        return
