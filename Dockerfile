# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Prevent Python from writing pyc files to disc (optional).
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED 1

# --- This is the key change ---
# Create the sandboxed workspace directory during the image build.
RUN mkdir -p /app/workspace

# Install dependencies for the controller/server.
# We copy only the pyproject.toml first to leverage Docker layer caching.
COPY server/pyproject.toml ./server/
RUN pip install --no-cache-dir ./server

# Install dependencies for the environment backend.
COPY environment/pyproject.toml ./environment/
RUN pip install --no-cache-dir ./environment

# Copy the rest of your application code.
COPY server/ ./server/
COPY environment/ ./environment/

# Set the port the environment server will run on.
ENV ENV_SERVER_PORT=8005

# Command to run both the backend and the MCP controller.
CMD ["sh", "-c", "uvicorn environment.server:app --host 0.0.0.0 --port $ENV_SERVER_PORT --log-level warning & python -m server.main"]