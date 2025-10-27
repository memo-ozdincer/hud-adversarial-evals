# In TEST0/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Create the sandboxed workspace directory.
RUN mkdir -p /app/workspace

# Install all dependencies from the single pyproject.toml
COPY server/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy the entire application code.
COPY server/ ./

ENV ENV_SERVER_PORT=8005

# Updated CMD to point to the new locations
CMD ["sh", "-c", "uvicorn backend:app --host 0.0.0.0 --port $ENV_SERVER_PORT --log-level warning & python -m main"]