from datetime import date
from app import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    program = db.Column(db.String(80), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    target_weight = db.Column(db.Float)
    target_adherence = db.Column(db.Integer, default=80)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    week = db.Column(db.String(30), nullable=False)
    adherence = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Date, default=date.today, nullable=False)
    client = db.relationship("Client", backref=db.backref("progress_entries", lazy=True))

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    workout_date = db.Column(db.Date, default=date.today, nullable=False)
    workout_type = db.Column(db.String(100), nullable=False)
    duration_min = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, default="")
    client = db.relationship("Client", backref=db.backref("workouts", lazy=True))

class BodyMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    recorded_on = db.Column(db.Date, default=date.today, nullable=False)
    weight = db.Column(db.Float)
    waist = db.Column(db.Float)
    bodyfat = db.Column(db.Float)
    client = db.relationship("Client", backref=db.backref("metrics", lazy=True))
