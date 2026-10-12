"""Route and persistence tests for the ACEest Flask application."""
from app import db
from app.models import BodyMetric, Client, Progress, Workout
from app.programs import PROGRAMS


def client_form(**overrides):
    values = {
        "name": "New Client",
        "age": "28",
        "height": "175",
        "weight": "72.5",
        "program": "Fat Loss (FL) – 3 day",
        "target_weight": "68",
        "target_adherence": "85",
    }
    values.update(overrides)
    return values


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest" in response.data or b"Dashboard" in response.data


def test_client_directory_loads(client):
    response = client.get("/clients/")
    assert response.status_code == 200


def test_add_client_persists_and_calculates_calories(app, client):
    response = client.post("/clients/add", data=client_form(), follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        item = Client.query.filter_by(name="New Client").one()
        assert item.calories == round(72.5 * PROGRAMS[item.program]["factor"])
        assert item.target_weight == 68
        assert item.target_adherence == 85


def test_add_client_rejects_invalid_age(client):
    response = client.post("/clients/add", data=client_form(age="0"), follow_redirects=True)
    assert response.status_code == 200
    assert b"valid age" in response.data or b"valid age, height" in response.data


def test_add_client_rejects_unknown_program(client):
    response = client.post("/clients/add", data=client_form(program="Not a program"), follow_redirects=True)
    assert response.status_code == 200
    assert b"valid fitness program" in response.data


def test_duplicate_client_name_is_rejected(client, sample_client):
    response = client.post("/clients/add", data=client_form(name=sample_client.name), follow_redirects=True)
    assert response.status_code == 200
    assert b"unique name" in response.data


def test_client_detail_displays_profile(client, sample_client):
    response = client.get(f"/clients/{sample_client.id}")
    assert response.status_code == 200
    assert b"Test Client" in response.data


def test_edit_client_updates_profile_and_calories(app, client, sample_client):
    response = client.post(
        f"/clients/{sample_client.id}/edit",
        data=client_form(name="Updated Client", weight="80", program="Muscle Gain (MG) – PPL"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        item = db.session.get(Client, sample_client.id)
        assert item.name == "Updated Client"
        assert item.calories == round(80 * PROGRAMS["Muscle Gain (MG) – PPL"]["factor"])


def test_add_weekly_progress(client, app, sample_client):
    response = client.post(f"/progress/client/{sample_client.id}/add", data={"adherence": "90"})
    assert response.status_code == 302
    with app.app_context():
        entry = Progress.query.filter_by(client_id=sample_client.id).one()
        assert entry.adherence == 90
        assert entry.week.startswith("Week ")


def test_progress_rejects_adherence_out_of_range(client, app, sample_client):
    client.post(f"/progress/client/{sample_client.id}/add", data={"adherence": "101"})
    with app.app_context():
        assert Progress.query.filter_by(client_id=sample_client.id).count() == 0


def test_add_workout(client, app, sample_client):
    response = client.post(
        f"/progress/client/{sample_client.id}/workout",
        data={"workout_type": "Strength", "duration_min": "45", "notes": "Upper body"},
    )
    assert response.status_code == 302
    with app.app_context():
        workout = Workout.query.filter_by(client_id=sample_client.id).one()
        assert workout.workout_type == "Strength"
        assert workout.duration_min == 45
        assert workout.notes == "Upper body"


def test_workout_rejects_missing_type(client, app, sample_client):
    client.post(f"/progress/client/{sample_client.id}/workout", data={"workout_type": "", "duration_min": "30"})
    with app.app_context():
        assert Workout.query.filter_by(client_id=sample_client.id).count() == 0


def test_add_body_metrics(client, app, sample_client):
    response = client.post(
        f"/progress/client/{sample_client.id}/metrics",
        data={"weight": "69.5", "waist": "82", "bodyfat": "21.5"},
    )
    assert response.status_code == 302
    with app.app_context():
        metric = BodyMetric.query.filter_by(client_id=sample_client.id).one()
        assert metric.weight == 69.5
        assert metric.waist == 82
        assert metric.bodyfat == 21.5


def test_body_metrics_reject_empty_submission(client, app, sample_client):
    client.post(f"/progress/client/{sample_client.id}/metrics", data={"weight": "", "waist": "", "bodyfat": ""})
    with app.app_context():
        assert BodyMetric.query.filter_by(client_id=sample_client.id).count() == 0


def test_delete_client_removes_associated_records(client, app, sample_client):
    with app.app_context():
        db.session.add(Progress(client_id=sample_client.id, week="Week 01 - 2026", adherence=80))
        db.session.add(Workout(client_id=sample_client.id, workout_type="Cardio", duration_min=20))
        db.session.add(BodyMetric(client_id=sample_client.id, weight=70))
        db.session.commit()
        client_id = sample_client.id

    response = client.post(f"/clients/{client_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Client, client_id) is None
        assert Progress.query.filter_by(client_id=client_id).count() == 0
        assert Workout.query.filter_by(client_id=client_id).count() == 0
        assert BodyMetric.query.filter_by(client_id=client_id).count() == 0
