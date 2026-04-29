import re
from datetime import datetime


class ValidationError(Exception):
    pass


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def required_text(value, field_name):
    clean_value = (value or "").strip()
    if not clean_value:
        raise ValidationError(f"El campo '{field_name}' es obligatorio.")
    return clean_value


def valid_email(value):
    email = required_text(value, "correo electronico").lower()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Ingresa un correo electronico valido.")
    return email


def positive_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo '{field_name}' debe ser un numero entero.") from exc

    if parsed <= 0:
        raise ValidationError(f"El campo '{field_name}' debe ser mayor a cero.")
    return parsed


def positive_float(value, field_name):
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo '{field_name}' debe ser numerico.") from exc

    if parsed < 0:
        raise ValidationError(f"El campo '{field_name}' no puede ser negativo.")
    return parsed


def parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo '{field_name}' debe tener formato YYYY-MM-DD.") from exc
