from datetime import date, timedelta

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.tracker import HabitTrackerFactory


class Habit(db.Model, TimestampMixin):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    metric_type = db.Column(db.String(20), nullable=False, default="quantity")
    target_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default="daily")
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="habits")

    logs = db.relationship(
        "HabitLog",
        back_populates="habit",
        cascade="all, delete-orphan",
        order_by="desc(HabitLog.log_date)",
        lazy=True,
    )

    def tracker(self):
        return HabitTrackerFactory.create(self.metric_type, self.target_value)

    def value_for_date(self, reference_date=None):
        reference_date = reference_date or date.today()
        daily_logs = [log for log in self.logs if log.log_date == reference_date]
        if self.metric_type == "boolean":
            return 1 if any(log.value > 0 for log in daily_logs) else 0
        return sum(log.value for log in daily_logs)

    def completion_percentage(self, reference_date=None):
        return round(
            self.tracker().calculate_progress(self.value_for_date(reference_date)),
            2,
        )

    def current_streak(self):
        streak = 0
        current_day = date.today()
        while self.tracker().is_completed(self.value_for_date(current_day)):
            streak += 1
            current_day -= timedelta(days=1)
        return streak

    def weekly_average(self):
        total = 0.0
        for day_offset in range(7):
            current_day = date.today() - timedelta(days=day_offset)
            total += self.completion_percentage(current_day)
        return round(total / 7, 2)

    def recent_logs(self, limit=5):
        return self.logs[:limit]

    def __str__(self):
        return f"{self.title} ({self.category})"
