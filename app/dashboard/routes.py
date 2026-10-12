from flask import render_template
from app.dashboard import bp
from app.models import Client, Progress, Workout

@bp.get("/")
def index():
    return render_template(
        "dashboard.html",
        client_count=Client.query.count(),
        progress_count=Progress.query.count(),
        workout_count=Workout.query.count(),
        clients=Client.query.order_by(Client.name).limit(8).all()
    )
