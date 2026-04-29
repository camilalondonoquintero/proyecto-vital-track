from datetime import date

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.extensions import db
from app.models import Habit, HabitLog
from app.services.habit_service import HabitService
from app.services.tips_service import obtener_tip_saludable
from app.utils import ValidationError, login_required


web_bp = Blueprint("web", __name__)


def get_owned_habit(habit_id):
    habit = db.session.get(Habit, habit_id)
    if habit is None or habit.user_id != g.user.id:
        return None
    return habit


def get_owned_log(log_id):
    log = db.session.get(HabitLog, log_id)
    if log is None or log.habit.user_id != g.user.id:
        return None
    return log


@web_bp.get("/")
def home():
    if g.user:
        return redirect(url_for("web.dashboard"))
    return render_template("home.html")


@web_bp.post("/auth/register")
def register():
    try:
        user, message = HabitService.register_user(request.form)
        session.clear()
        session["user_id"] = user.id
        flash(message, "success")
        return redirect(url_for("web.dashboard"))
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("web.home"))


@web_bp.post("/auth/login")
def login():
    try:
        user = HabitService.authenticate_user(request.form)
        session.clear()
        session["user_id"] = user.id
        flash(f"Bienvenido de nuevo, {user.first_name}.", "success")
        return redirect(url_for("web.dashboard"))
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("web.home"))


@web_bp.post("/auth/logout")
@login_required
def logout():
    session.clear()
    flash("Tu sesion se cerro correctamente.", "success")
    return redirect(url_for("web.home"))


@web_bp.get("/dashboard")
@login_required
def dashboard():
    summary = HabitService.user_dashboard_summary(g.user)
    tip_saludable = obtener_tip_saludable()

    return render_template(
        "dashboard.html",
        user=g.user,
        summary=summary,
        tip_saludable=tip_saludable,
        today=date.today(),
    )


@web_bp.get("/profile")
@login_required
def profile():
    return render_template("user_detail.html", user=g.user)


@web_bp.get("/users/<int:user_id>")
@login_required
def user_detail(user_id):
    if user_id != g.user.id:
        flash("Solo puedes acceder a tu propio perfil.", "error")
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.profile"))


@web_bp.post("/profile/update")
@login_required
def update_profile():
    try:
        _, message = HabitService.update_user(g.user, request.form)
        flash(message, "success")
    except ValidationError as exc:
        flash(str(exc), "error")
    return redirect(url_for("web.profile"))


@web_bp.post("/profile/delete")
@login_required
def delete_profile():
    HabitService.delete_user(g.user)
    session.clear()
    flash("Tu cuenta y tus habitos fueron eliminados.", "success")
    return redirect(url_for("web.home"))


@web_bp.post("/habits/create")
@login_required
def create_habit():
    form_data = request.form.to_dict()
    form_data["user_id"] = str(g.user.id)

    try:
        _, message = HabitService.create_habit(form_data)
        flash(message, "success")
    except ValidationError as exc:
        flash(str(exc), "error")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/habits/<int:habit_id>/update")
@login_required
def update_habit(habit_id):
    habit = get_owned_habit(habit_id)
    if habit is None:
        flash("El habito solicitado no existe o no te pertenece.", "error")
        return redirect(url_for("web.dashboard"))

    try:
        _, message = HabitService.update_habit(habit, request.form)
        flash(message, "success")
    except ValidationError as exc:
        flash(str(exc), "error")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/habits/<int:habit_id>/delete")
@login_required
def delete_habit(habit_id):
    habit = get_owned_habit(habit_id)
    if habit is None:
        flash("El habito solicitado no existe o no te pertenece.", "error")
        return redirect(url_for("web.dashboard"))

    message = HabitService.delete_habit(habit)
    flash(message, "success")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/habits/<int:habit_id>/logs/create")
@login_required
def create_log(habit_id):
    habit = get_owned_habit(habit_id)
    if habit is None:
        flash("El habito solicitado no existe o no te pertenece.", "error")
        return redirect(url_for("web.dashboard"))

    try:
        _, message = HabitService.create_log(habit, request.form)
        flash(message, "success")
    except ValidationError as exc:
        flash(str(exc), "error")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/logs/<int:log_id>/delete")
@login_required
def delete_log(log_id):
    log = get_owned_log(log_id)
    if log is None:
        flash("El registro solicitado no existe o no te pertenece.", "error")
        return redirect(url_for("web.dashboard"))

    message = HabitService.delete_log(log)
    flash(message, "success")
    return redirect(url_for("web.dashboard"))
