from datetime import date

from app.extensions import db
from app.models.base import TimestampMixin


class HabitLog(db.Model, TimestampMixin):
    __tablename__ = "habit_logs"

    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today)
    value = db.Column(db.Float, nullable=False, default=0)
    note = db.Column(db.String(255), nullable=True)

    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    habit = db.relationship("Habit", back_populates="logs")

    def __str__(self):
        return f"Registro {self.log_date} - {self.value}"
