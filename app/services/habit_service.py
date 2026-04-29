from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Habit, HabitLog, User
from app.utils.validators import (
    ValidationError,
    parse_date,
    positive_float,
    positive_int,
    required_text,
    valid_email,
)


class HabitService:
    ALLOWED_METRIC_TYPES = {"quantity", "duration", "boolean"}
    ALLOWED_FREQUENCIES = {"daily", "weekly"}

    @staticmethod
    def register_user(form_data):
        password = HabitService._validate_passwords(
            form_data.get("password"),
            form_data.get("confirm_password"),
        )

        user = User(
            full_name=required_text(form_data.get("full_name"), "nombre completo"),
            email=valid_email(form_data.get("email")),
            age=positive_int(form_data.get("age"), "edad"),
            wellness_goal=required_text(form_data.get("wellness_goal"), "objetivo de bienestar"),
        )
        user.set_password(password)
        db.session.add(user)
        return HabitService._commit_entity(user, "Cuenta creada correctamente. Ya puedes entrar a tu panel.")

    @staticmethod
    def authenticate_user(form_data):
        email = valid_email(form_data.get("email"))
        password = required_text(form_data.get("password"), "contrasena")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            raise ValidationError("Correo o contrasena incorrectos.")
        return user

    @staticmethod
    def update_user(user, form_data):
        user.full_name = required_text(form_data.get("full_name"), "nombre completo")
        user.email = valid_email(form_data.get("email"))
        user.age = positive_int(form_data.get("age"), "edad")
        user.wellness_goal = required_text(
            form_data.get("wellness_goal"),
            "objetivo de bienestar",
        )

        new_password = (form_data.get("new_password") or "").strip()
        confirm_password = (form_data.get("confirm_password") or "").strip()
        if new_password or confirm_password:
            user.set_password(HabitService._validate_passwords(new_password, confirm_password))

        return HabitService._commit_entity(user, "Usuario actualizado correctamente.")

    @staticmethod
    def delete_user(user):
        db.session.delete(user)
        db.session.commit()
        return "Usuario eliminado correctamente."

    @staticmethod
    def create_habit(form_data):
        user_id = positive_int(form_data.get("user_id"), "usuario")

        metric_type = required_text(form_data.get("metric_type"), "tipo de seguimiento")
        frequency = required_text(form_data.get("frequency"), "frecuencia")
        HabitService._validate_habit_options(metric_type, frequency)

        habit = Habit(
            user_id=user_id,
            title=required_text(form_data.get("title"), "titulo"),
            description=required_text(form_data.get("description"), "descripcion"),
            category=required_text(form_data.get("category"), "categoria"),
            metric_type=metric_type,
            target_value=max(positive_float(form_data.get("target_value"), "meta diaria"), 1),
            unit=required_text(form_data.get("unit"), "unidad"),
            frequency=frequency,
        )
        db.session.add(habit)
        return HabitService._commit_entity(habit, "Habito creado correctamente.")

    @staticmethod
    def update_habit(habit, form_data):
        metric_type = required_text(form_data.get("metric_type"), "tipo de seguimiento")
        frequency = required_text(form_data.get("frequency"), "frecuencia")
        HabitService._validate_habit_options(metric_type, frequency)

        habit.title = required_text(form_data.get("title"), "titulo")
        habit.description = required_text(form_data.get("description"), "descripcion")
        habit.category = required_text(form_data.get("category"), "categoria")
        habit.metric_type = metric_type
        habit.target_value = max(positive_float(form_data.get("target_value"), "meta diaria"), 1)
        habit.unit = required_text(form_data.get("unit"), "unidad")
        habit.frequency = frequency
        habit.is_active = form_data.get("is_active") == "on"
        return HabitService._commit_entity(habit, "Habito actualizado correctamente.")

    @staticmethod
    def delete_habit(habit):
        db.session.delete(habit)
        db.session.commit()
        return "Habito eliminado correctamente."

    @staticmethod
    def create_log(habit, form_data):
        log = HabitLog(
            habit_id=habit.id,
            log_date=parse_date(form_data.get("log_date"), "fecha"),
            value=positive_float(form_data.get("value"), "avance"),
            note=(form_data.get("note") or "").strip() or None,
        )
        db.session.add(log)
        return HabitService._commit_entity(log, "Registro agregado correctamente.")

    @staticmethod
    def delete_log(log):
        db.session.delete(log)
        db.session.commit()
        return "Registro eliminado correctamente."

    @staticmethod
    def dashboard_summary():
        users = User.query.all()
        habits = Habit.query.all()
        total_progress = sum(habit.completion_percentage() for habit in habits)
        average_progress = round(total_progress / len(habits), 2) if habits else 0
        completed_today = len([habit for habit in habits if habit.completion_percentage() >= 100])

        return {
            "users": len(users),
            "habits": len(habits),
            "completed_today": completed_today,
            "average_progress": average_progress,
        }

    @staticmethod
    def user_dashboard_summary(user):
        habits = list(user.habits)
        completed_today = len([habit for habit in habits if habit.completion_percentage() >= 100])
        average_progress = (
            round(sum(habit.completion_percentage() for habit in habits) / len(habits), 2)
            if habits
            else 0
        )

        return {
            "habits": len(habits),
            "completed_today": completed_today,
            "average_progress": average_progress,
            "active_streaks": len([habit for habit in habits if habit.current_streak() > 0]),
        }

    @staticmethod
    def _commit_entity(entity, success_message):
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ValidationError(
                "No se pudo guardar la informacion. Verifica que el correo no este repetido."
            ) from exc
        return entity, success_message

    @staticmethod
    def _validate_habit_options(metric_type, frequency):
        if metric_type not in HabitService.ALLOWED_METRIC_TYPES:
            raise ValidationError("El tipo de seguimiento seleccionado no es valido.")
        if frequency not in HabitService.ALLOWED_FREQUENCIES:
            raise ValidationError("La frecuencia seleccionada no es valida.")

    @staticmethod
    def _validate_passwords(password, confirm_password):
        password = required_text(password, "contrasena")
        confirm_password = required_text(confirm_password, "confirmacion de contrasena")
        if len(password) < 6:
            raise ValidationError("La contrasena debe tener al menos 6 caracteres.")
        if password != confirm_password:
            raise ValidationError("Las contrasenas no coinciden.")
        return password
