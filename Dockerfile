# Separate test target keeps development dependencies out of the runtime image.
FROM python:3.12-slim AS test
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements-dev.txt ./requirements-dev.txt
RUN pip install --upgrade pip && pip install -r requirements-dev.txt
COPY . .
CMD ["python", "-m", "pytest", "-v"]

# Portable runtime image for ACEest Fitness & Performance.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_URL=sqlite:////data/aceest_fitness.db

WORKDIR /app

# Install dependencies before copying application code for better layer caching.
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Persist SQLite data outside the image and run as a non-root user.
RUN mkdir -p /data && useradd --system --uid 10001 --create-home appuser \
    && chown -R appuser:appuser /app /data
USER appuser

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "--access-logfile=-", "--error-logfile=-", "run:app"]
