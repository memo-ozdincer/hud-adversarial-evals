# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Prevent Python from writing pyc files to disc (optional but good practice).
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- FIX: Create the sandboxed workspace directory during the image build ---
RUN mkdir -p /app/workspace

# Install all dependencies from the single pyproject.toml
# We copy only the pyproject.toml first to leverage Docker layer caching.
COPY server/pyproject.toml ./pyproject.toml
COPY server/uv.lock ./uv.lock
RUN pip install --no-cache-dir -e .

# Copy the entire application code into the WORKDIR (/app).
COPY server/ .

# Set the port the environment server will run on.
ENV ENV_SERVER_PORT=8005

# --- FIX: Updated CMD to point to the new, simplified locations ---
CMD ["sh", "-c", "uvicorn backend:app --host 0.0.0.0 --port $ENV_SERVER_PORT --log-level warning & python main.py"]