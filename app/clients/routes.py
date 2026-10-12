from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Client
from app.programs import PROGRAMS
from app.clients import bp

@bp.get("/")
def index():
    return render_template("clients.html", clients=Client.query.order_by(Client.name).all())

@bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            age = int(request.form.get("age", "0"))
            height = float(request.form.get("height", "0"))
            weight = float(request.form.get("weight", "0"))
            program = request.form.get("program", "")
            target_raw = request.form.get("target_weight", "").strip()
            target_adherence = int(request.form.get("target_adherence", "80"))
            if not name or program not in PROGRAMS:
                raise ValueError("Enter a name and choose a valid fitness program.")
            if not 1 <= age <= 110 or height <= 0 or weight <= 0:
                raise ValueError("Enter a valid age, height, and weight.")
            if not 0 <= target_adherence <= 100:
                raise ValueError("Target adherence must be between 0 and 100.")
            target_weight = float(target_raw) if target_raw else None
            if target_weight is not None and target_weight <= 0:
                raise ValueError("Target weight must be positive.")
            calories = round(weight * PROGRAMS[program]["factor"])
            client = Client(name=name, age=age, height=height, weight=weight,
                program=program, calories=calories, target_weight=target_weight,
                target_adherence=target_adherence)
            db.session.add(client)
            db.session.commit()
            flash("Client profile saved.", "success")
            return redirect(url_for("clients.detail", client_id=client.id))
        except ValueError as exc:
            flash(str(exc), "error")
        except IntegrityError:
            db.session.rollback()
            flash("A client with that name already exists. Use a unique name.", "error")
    return render_template("client_form.html", client=None, programs=PROGRAMS)

@bp.get("/<int:client_id>")
def detail(client_id):
    from app.models import Progress, Workout, BodyMetric
    client = db.get_or_404(Client, client_id)
    progress = Progress.query.filter_by(client_id=client.id).order_by(Progress.id.desc()).limit(12).all()
    workouts = Workout.query.filter_by(client_id=client.id).order_by(Workout.id.desc()).limit(10).all()
    metrics = BodyMetric.query.filter_by(client_id=client.id).order_by(BodyMetric.id.desc()).limit(10).all()
    return render_template("client_detail.html", client=client, progress=progress, workouts=workouts, metrics=metrics, programs=PROGRAMS)

@bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
def edit(client_id):
    client = db.get_or_404(Client, client_id)
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            age = int(request.form.get("age", "0"))
            height = float(request.form.get("height", "0"))
            weight = float(request.form.get("weight", "0"))
            program = request.form.get("program", "")
            target_raw = request.form.get("target_weight", "").strip()
            target_adherence = int(request.form.get("target_adherence", "80"))
            if not name or program not in PROGRAMS or not 1 <= age <= 110 or height <= 0 or weight <= 0:
                raise ValueError("Check name, program, age, height, and weight.")
            if not 0 <= target_adherence <= 100:
                raise ValueError("Target adherence must be between 0 and 100.")
            client.name, client.age, client.height, client.weight = name, age, height, weight
            client.program = program
            client.calories = round(weight * PROGRAMS[program]["factor"])
            client.target_weight = float(target_raw) if target_raw else None
            client.target_adherence = target_adherence
            db.session.commit()
            flash("Client profile updated.", "success")
            return redirect(url_for("clients.detail", client_id=client.id))
        except ValueError as exc:
            flash(str(exc), "error")
        except IntegrityError:
            db.session.rollback()
            flash("That client name is already in use.", "error")
    return render_template("client_form.html", client=client, programs=PROGRAMS)

@bp.post("/<int:client_id>/delete")
def delete(client_id):
    from app.models import Progress, Workout, BodyMetric
    client = db.get_or_404(Client, client_id)
    Progress.query.filter_by(client_id=client.id).delete()
    Workout.query.filter_by(client_id=client.id).delete()
    BodyMetric.query.filter_by(client_id=client.id).delete()
    db.session.delete(client)
    db.session.commit()
    flash("Client and associated progress records deleted.", "success")
    return redirect(url_for("clients.index"))
