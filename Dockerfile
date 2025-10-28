### Final Corrected Dockerfile

FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

COPY server/pyproject.toml ./server/
COPY server/uv.lock ./server/
WORKDIR /app/server
RUN pip install --no-cache-dir -e .
WORKDIR /app

COPY server/ ./server/

# --- FIX: Create a dedicated directory for logs and other outputs ---
# This directory will be used for the volume mount.
RUN mkdir /output

ENV ENV_SERVER_PORT=8005
CMD ["python", "server/main.py"]