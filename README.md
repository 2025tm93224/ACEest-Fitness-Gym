# ACEest Fitness & Performance — Flask Edition

This modular web application adapts the supplied Tkinter/SQLite baseline into a browser-based Flask app.

## Included
- Dashboard and client directory
- Create, edit, view, and delete client profiles
- Baseline fitness programs and estimated calories (`weight × program factor`)
- Weekly adherence logging
- Workout logging and history
- Body metric logging (weight, waist, body-fat percentage)
- SQLite persistence using Flask-SQLAlchemy
- Flask application factory and Blueprints

## Run
Requires Python 3.10+.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install and start:
```bash
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000.

## Structure
- `app/__init__.py`: application factory, extension setup, blueprint registration
- `app/models.py`: client, progress, workout, and body metric models
- `app/programs.py`: baseline program data and calorie factors
- `app/dashboard/`: dashboard routes
- `app/clients/`: client CRUD and profile routes
- `app/progress/`: adherence, workout, and body metric endpoints
- `app/templates/`: Jinja templates
- `app/static/style.css`: responsive dark/gold styling

## Important notes
The calorie value deliberately preserves the baseline calculation; it is only a rough program-specific estimate and not individualized medical advice. Program descriptions and nutrition notes are general examples, not prescriptions.

This is a starter/demo application. Before production, add authentication and authorization, CSRF protection, migrations, automated tests, secure secret management, logging, backups, and a production WSGI server. Do not use Flask's debug server in production. The database schema is initialized with `create_all()`; this does not migrate an existing Tkinter database automatically.

## Unit testing with Pytest

Install the application and test dependencies in your virtual environment:

```bash
pip install -r requirements-dev.txt
```

Run the complete test suite from the project root:

```bash
python -m pytest
```

Run one test module or show each test result:

```bash
python -m pytest tests/test_programs.py -v
python -m pytest -v
```

The tests use an isolated in-memory SQLite database and Flask's test client, so they do not use or overwrite the local development database. Coverage includes program configuration and calorie-factor calculations, dashboard and client pages, client create/edit validation and persistence, duplicate-name handling, weekly adherence, workout logging, body metrics, and cascading record deletion. Add tests for every new feature or bug fix before merging its branch into `main`.

## Docker containerization

The image uses Python 3.12, installs runtime dependencies, runs Gunicorn as a non-root user, and stores the SQLite database in `/data`. The named Docker volume keeps the database when the container is recreated. Pytest and other development files are excluded from the image build context where appropriate.

Install Docker Engine or a compatible Docker CLI/Compose setup on the host, then from the project root:

```bash
# Set a strong secret for this shell session; do not commit it to Git.
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build -d
docker compose ps
docker compose logs -f web
```

Open <http://localhost:8000>. Stop the service with `docker compose down`. The named `aceest_data` volume is retained by default; `docker compose down -v` deletes that volume and its database, so use it only when you intentionally want to remove the data.

To run the Pytest suite inside a dedicated test image (separate from the production runtime image):

```bash
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test
```

The runtime image excludes Pytest and other development dependencies. You can also run tests on the Rocky Linux host using `pip install -r requirements-dev.txt && python -m pytest -v` inside your virtual environment.

For Rocky Linux, confirm the Docker Engine and Compose plugin are installed and the Docker service is running before using `docker compose`. If your lab uses Podman, these files may work with compatible Compose tooling, but command availability depends on the lab setup. The application is a learning/demo project; production deployment still requires authentication/authorization, CSRF protection, migrations, backups, and secure secret management.
