from flask import redirect, url_for
from flask_login import current_user
from functools import wraps


def roles_required(*roles):
    def wrapper(view_function):
        @wraps(view_function)
        def decorator(*args, **kwargs):
            if set(roles).issubset(set([r.name for r in current_user.roles])):
                return view_function(*args, **kwargs)
            else:
                return redirect(url_for("auth.denied", required_clearance=roles))
        return decorator
    return wrapper