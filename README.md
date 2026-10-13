# ACEest Fitness & Performance

A modular Flask web application for managing gym clients and recording fitness progress. This project adapts the supplied Tkinter/SQLite baseline into a browser-based application and demonstrates a development workflow using Git, Pytest, Docker, Jenkins, and GitHub Actions.

## Contents

- [Features](#features)
- [Technology stack](#technology-stack)
- [Project layout](#project-layout)
- [Local setup and execution](#local-setup-and-execution)
- [Manual testing](#manual-testing)
- [Docker usage](#docker-usage)
- [CI integration](#ci-integration)
  - [GitHub Actions](#github-actions)
  - [Jenkins](#jenkins)
- [Git workflow](#git-workflow)
- [Limitations and production considerations](#limitations-and-production-considerations)

## Features

- Dashboard showing client and activity summaries.
- Create, view, edit, and delete client profiles.
- Fitness program information and a rough program-specific calorie estimate (`weight × program factor`).
- Weekly adherence tracking.
- Workout logging and history.
- Body metric records, including weight, waist, and body-fat percentage.
- SQLite persistence through Flask-SQLAlchemy.
- Flask application factory and Blueprints for modular routes.

## Technology stack

- Python 3.10+ for local development; the Docker image uses Python 3.12.
- Flask and Flask-SQLAlchemy.
- SQLite for the local database.
- Pytest for automated tests and Flake8 for linting.
- Docker / Docker Compose for containerized execution.
- Jenkins and GitHub Actions for CI validation.

## Project layout

```text
aceest_flask_app/
├── app/
│   ├── clients/              # Client profile routes
│   ├── dashboard/           # Dashboard route
│   ├── progress/             # Adherence, workout, and body metric routes
│   ├── templates/            # Jinja templates
│   ├── static/               # CSS assets
│   ├── models.py             # SQLAlchemy models
│   └── programs.py           # Fitness program definitions
├── tests/                    # Pytest test suite
├── .github/workflows/
│   ├── main.yml              # Build, lint, Docker, and containerized tests
│   └── tests.yml             # Additional test workflow
├── Dockerfile                # Test and runtime image targets
├── compose.yaml              # Local container configuration
├── Jenkinsfile               # Jenkins declarative pipeline
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Runtime plus test/lint dependencies
├── config.py
├── run.py
└── README.md
```

## Local setup and execution

### Rocky Linux

Install Python, pip, and virtual-environment support:

```bash
sudo dnf install -y python3 python3-pip python3-devel
python3 --version
```

Extract the project ZIP, then change into the project directory. For example:

```bash
unzip aceest_flask_app_github_actions.zip
cd aceest_flask_app
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install application dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the development server:

```bash
python run.py
```

Open <http://127.0.0.1:5000> in a browser. Stop the server with `Ctrl+C`; leave the virtual environment with `deactivate`.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run.py
```

## Manual testing

Activate the project's virtual environment, then install development dependencies. This installs the runtime requirements along with Pytest and Flake8:

```bash
python -m pip install -r requirements-dev.txt
```

Run the complete test suite:

```bash
python -m pytest -v
```

Run a specific test module:

```bash
python -m pytest tests/test_programs.py -v
python -m pytest tests/test_app_routes.py -v
```

Run the syntax and lint checks used by CI:

```bash
python -m compileall -q app run.py config.py tests
python -m flake8 app run.py config.py tests --count --show-source --statistics --max-line-length=100 --extend-ignore=E203,W503
python -m pip check
```

The tests use an isolated in-memory SQLite database and Flask's test client; they are designed not to overwrite the local development database. The suite covers program configuration, routes, client validation and persistence, adherence, workout logging, body metrics, and related record deletion. Add or update tests when implementing a feature or fixing a bug.

## Docker usage

Install Docker Engine and the Docker Compose plugin, then confirm the Docker daemon is running. On Rocky Linux, use the installation method approved for your lab. Docker daemon access is privileged; do not make `/var/run/docker.sock` writable by every local user.

From the project root, create a strong secret for the current shell session and start the service:

```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build -d
docker compose ps
docker compose logs -f web
```

Open <http://localhost:8000>. Stop the service with:

```bash
docker compose down
```

The Compose configuration uses a named volume (`aceest_data`) to persist the SQLite database when the container is stopped or recreated. `docker compose down -v` removes the volume and its data; use it only when you intentionally want to delete the database.

Build and run the test target to execute Pytest inside a container:

```bash
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test
```

Build the runtime image without starting it:

```bash
docker build --target runtime -t aceest-fitness:local .
```

## CI integration

Both CI systems provide repeatable validation, but they are configured independently. Keep `main` as the stable branch and require checks to pass before merging changes.

### GitHub Actions

Workflow file: `.github/workflows/main.yml`

**Triggers:** every `push` and every `pull_request` event.

The workflow uses GitHub-hosted Ubuntu runners and Python 3.12. It has two dependent jobs:

1. **Build and lint** — checks out the code, installs `requirements-dev.txt`, compiles the Python source with `compileall`, and runs Flake8.
2. **Assemble Docker images** — runs only if build/lint passes; builds the Docker `runtime` and `test` targets, then runs the Pytest suite inside the test container.

A failed lint check, Docker build, or test command fails the workflow. Images are built for validation only: this workflow does not publish them to a registry or deploy the application.

**To enable it:** commit `.github/workflows/main.yml` and the project files, push them to GitHub, and open the repository's **Actions** tab. GitHub Actions runs the workflow on subsequent pushes and pull requests. Review job logs and test output for failures.

### Jenkins

Pipeline file: `Jenkinsfile`

The Jenkins declarative pipeline checks out the revision configured in the Jenkins job, creates a fresh Python virtual environment, installs development dependencies, compiles the application, checks installed dependencies with `pip check`, runs Pytest, publishes a JUnit-format test report, and builds the Docker runtime image. A failed validation stage prevents the pipeline from completing successfully.

**Jenkins agent prerequisites:** Git, Python 3 with `venv`, pip, Docker CLI/daemon access, and network access to install dependencies. Docker access should be granted only through the lab's approved administration process because membership in the `docker` group is effectively root-level access.

**Configure a Jenkins Pipeline job:**

1. Push the project, including `Jenkinsfile`, to GitHub.
2. In Jenkins, choose **New Item**, enter a job name such as `aceest-fitness-build`, and select **Pipeline**.
3. Under **Pipeline**, select **Pipeline script from SCM** and choose **Git**.
4. Enter the GitHub repository URL, configure credentials if the repository is private, set the branch to the actual branch name (for example, `*/main`), and set **Script Path** to `Jenkinsfile`.
5. Save and select **Build Now**. Review the stage view, console log, and test report.
6. For automatic builds, configure a GitHub webhook and the appropriate GitHub hook trigger, or use SCM polling / a Multibranch Pipeline. A webhook requires GitHub to reach the Jenkins endpoint.

The Jenkins pipeline validates the build; it does not publish a Docker image or deploy the application. Registry publishing and deployment should be separate, controlled stages with credentials stored in Jenkins credentials management.

## Git workflow

Use `main` for stable code and short-lived branches for changes:

```bash
git switch main
git pull origin main
git switch -c feature/short-description
# Make changes and run tests
git add .
git commit -m "feat: describe the change"
git push -u origin feature/short-description
```

Open a pull request into `main`, review the changes, and wait for required CI checks before merging. Use descriptive commit prefixes such as `feat:`, `fix:`, `test:`, `docs:`, `ci:`, and `chore:`.

## Limitations and production considerations

- The calorie estimate intentionally preserves the baseline formula (`weight × program factor`). It is a rough program-specific estimate, not individualized medical advice. Program and nutrition descriptions are examples, not prescriptions.
- This project is a learning/demo application. Before production use, implement authentication and authorization, CSRF protection, database migrations, secure secret management, backups, monitoring, and an appropriate production deployment configuration.
- The schema is initialized with `create_all()`; this does not automatically migrate an existing database from the original Tkinter application.
- Do not commit secrets, local database files, or virtual environments. The Flask development server is for local development only; the Docker runtime uses Gunicorn.
