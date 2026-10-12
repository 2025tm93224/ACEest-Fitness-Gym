from datetime import date
from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Client, Progress, Workout, BodyMetric
from app.progress import bp

@bp.route("/client/<int:client_id>/add", methods=["POST"])
def add(client_id):
    client = db.get_or_404(Client, client_id)
    try:
        adherence = int(request.form.get("adherence", "-1"))
        if not 0 <= adherence <= 100:
            raise ValueError
    except ValueError:
        flash("Adherence must be between 0 and 100.", "error")
        return redirect(url_for("clients.detail", client_id=client.id))
    db.session.add(Progress(client_id=client.id, week=date.today().strftime("Week %U - %Y"), adherence=adherence))
    db.session.commit()
    flash("Weekly progress saved.", "success")
    return redirect(url_for("clients.detail", client_id=client.id))

@bp.route("/client/<int:client_id>/workout", methods=["POST"])
def add_workout(client_id):
    client = db.get_or_404(Client, client_id)
    workout_type = request.form.get("workout_type", "").strip()
    try:
        duration = int(request.form.get("duration_min", "0"))
        if not workout_type or not 0 <= duration <= 1440:
            raise ValueError
    except ValueError:
        flash("Enter a workout type and a valid duration.", "error")
        return redirect(url_for("clients.detail", client_id=client.id))
    db.session.add(Workout(client_id=client.id, workout_type=workout_type, duration_min=duration,
                           notes=request.form.get("notes", "").strip()))
    db.session.commit()
    flash("Workout logged.", "success")
    return redirect(url_for("clients.detail", client_id=client.id))

@bp.route("/client/<int:client_id>/metrics", methods=["POST"])
def add_metrics(client_id):
    client = db.get_or_404(Client, client_id)
    try:
        weight_raw = request.form.get("weight", "").strip()
        waist_raw = request.form.get("waist", "").strip()
        bodyfat_raw = request.form.get("bodyfat", "").strip()
        weight = float(weight_raw) if weight_raw else None
        waist = float(waist_raw) if waist_raw else None
        bodyfat = float(bodyfat_raw) if bodyfat_raw else None
        if all(v is None for v in (weight, waist, bodyfat)):
            raise ValueError
        if any(v is not None and v <= 0 for v in (weight, waist, bodyfat)):
            raise ValueError
        if bodyfat is not None and bodyfat > 100:
            raise ValueError
    except ValueError:
        flash("Enter at least one valid positive body metric; body fat must be at most 100%.", "error")
        return redirect(url_for("clients.detail", client_id=client.id))
    db.session.add(BodyMetric(client_id=client.id, weight=weight, waist=waist, bodyfat=bodyfat))
    db.session.commit()
    flash("Body metrics saved.", "success")
    return redirect(url_for("clients.detail", client_id=client.id))
