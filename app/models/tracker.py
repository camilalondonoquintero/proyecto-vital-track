class HabitTracker:
    def __init__(self, target_value):
        self._target_value = max(float(target_value or 1), 1.0)

    @property
    def target_value(self):
        return self._target_value

    def calculate_progress(self, current_value):
        raise NotImplementedError("Cada tracker debe definir su calculo.")

    def is_completed(self, current_value):
        return self.calculate_progress(current_value) >= 100

    def __str__(self):
        return f"{self.__class__.__name__}(meta={self.target_value})"


class CompletionTracker(HabitTracker):
    def calculate_progress(self, current_value):
        return 100.0 if float(current_value or 0) >= 1 else 0.0


class QuantityTracker(HabitTracker):
    def calculate_progress(self, current_value):
        current = max(float(current_value or 0), 0.0)
        return min((current / self.target_value) * 100, 100.0)


class DurationTracker(QuantityTracker):
    pass


class HabitTrackerFactory:
    TRACKERS = {
        "boolean": CompletionTracker,
        "quantity": QuantityTracker,
        "duration": DurationTracker,
    }

    @classmethod
    def create(cls, tracker_type, target_value):
        tracker_class = cls.TRACKERS.get(tracker_type, QuantityTracker)
        return tracker_class(target_value)
