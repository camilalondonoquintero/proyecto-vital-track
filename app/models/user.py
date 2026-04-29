from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import TimestampMixin


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    wellness_goal = db.Column(db.String(200), nullable=False)

    habits = db.relationship(
        "Habit",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @property
    def habits_count(self):
        return len(self.habits)

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else "Usuario"

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def __str__(self):
        return f"{self.full_name} ({self.email})"
