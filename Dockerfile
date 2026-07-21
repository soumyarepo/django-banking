# syntax=docker/dockerfile:1

# ==========================================
# Stage 1: Dependency builder
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
        -r requirements.txt


# ==========================================
# Stage 2: Runtime image
# ==========================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=banking_project.settings

WORKDIR /app

RUN groupadd --system django && \
    useradd \
        --system \
        --gid django \
        --create-home \
        django

COPY --from=builder /opt/venv /opt/venv

COPY --chown=django:django . /app

RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/staticfiles && \
    chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "banking_project.wsgi:application"]