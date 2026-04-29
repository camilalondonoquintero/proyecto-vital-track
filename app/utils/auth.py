from functools import wraps

from flask import flash, g, redirect, session, url_for

from app.extensions import db
from app.models import User


def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Inicia sesion para acceder a tu panel.", "error")
            return redirect(url_for("web.home"))
        return view(*args, **kwargs)

    return wrapped_view
