from flask import Flask, g
from sqlalchemy import inspect, text

from app.config.settings import Config
from app.controllers.web import web_bp
from app.extensions import db
from app.utils.auth import load_logged_in_user


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db.init_app(app)

    with app.app_context():
        from app.models import Habit, HabitLog, User  # noqa: F401

        db.create_all()
        run_lightweight_migrations()

    app.register_blueprint(web_bp)
    app.before_request(load_logged_in_user)
    register_context_processors(app)
    return app


def run_lightweight_migrations():
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    with db.engine.begin() as connection:
        if "password_hash" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))


def register_context_processors(app):
    @app.context_processor
    def inject_current_user():
        return {"current_user": getattr(g, "user", None)}
