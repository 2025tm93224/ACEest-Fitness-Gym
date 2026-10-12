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

## Jenkins BUILD pipeline

The root `Jenkinsfile` defines a declarative Jenkins pipeline that checks out the GitHub revision, creates a fresh Python virtual environment, installs `requirements-dev.txt`, compiles the Python modules, checks dependency consistency, runs Pytest as a quality gate, publishes JUnit results, and builds the Docker runtime image.

### Jenkins agent prerequisites

The Jenkins build agent must have Git, Python 3 with `venv`, pip, Docker CLI/Engine, and permission to access the Docker daemon. The Jenkins user should have Docker access through your lab's approved administration process; avoid making the Docker socket accessible to untrusted users because Docker access is effectively privileged. If Docker is not available on the agent, remove/disable the `Build Docker Image` stage or use a dedicated Docker-capable agent.

### Configure a Jenkins job

1. Push this project, including `Jenkinsfile`, to GitHub.
2. In Jenkins, install/enable **Pipeline**, **Git**, and **JUnit** support (the JUnit plugin is commonly installed by default).
3. Select **New Item → Pipeline**. Give it a name such as `aceest-fitness-build`.
4. Under **Pipeline**, choose **Pipeline script from SCM**; select **Git**, enter the GitHub repository URL, configure credentials if it is private, set the branch (for example `*/main`), and set **Script Path** to `Jenkinsfile`.
5. Save and click **Build Now**. Review the stage view and the **Test Result** report. A failing test or Docker build marks the pipeline as failed.
6. For automatic builds, configure a GitHub webhook to the Jenkins endpoint `/github-webhook/` and enable the GitHub hook trigger in the job, or configure a Multibranch Pipeline / SCM polling according to your lab's network setup. A webhook requires GitHub to be able to reach the Jenkins server.

### Quality gate behavior

The pipeline only reports success when dependency installation, Python compile checks, `pip check`, all Pytest tests, and the Docker runtime image build succeed. It does not push an image to a registry or deploy the app; those should be separate controlled pipeline stages with credentials managed in Jenkins, not hard-coded in the repository.
