"""Evolved FastAPI environment server with file system capabilities."""

from fastapi import FastAPI, HTTPException
import logging
import sys
import os

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
)

app = FastAPI(title="Evolved Environment API")

# --- State Management ---
_count = 0
WORKSPACE_DIR = "/app/workspace" # The agent's sandboxed directory inside the container

# Ensure the workspace directory exists on startup
os.makedirs(WORKSPACE_DIR, exist_ok=True)


# --- API Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/act")
def act():
    global _count
    _count += 1
    return {"count": _count}

@app.post("/reset")
def reset():
    global _count
    _count = 0
    # Also clean the workspace on reset for task isolation
    for filename in os.listdir(WORKSPACE_DIR):
        file_path = os.path.join(WORKSPACE_DIR, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return {"ok": True}

@app.get("/state")
def state():
    return {"count": _count}

# --- NEW: File System Endpoints ---
@app.post("/files/write")
async def write_file_endpoint(data: dict):
    filename = data.get("filename")
    content = data.get("content")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # SECURITY: Prevent path traversal attacks by only using the base name of the file
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))

    with open(safe_path, "w") as f:
        f.write(content or "")
    return {"status": "success", "filename": filename}

@app.get("/files/read/{filename}")
async def read_file_endpoint(filename: str):
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File not found.")
    with open(safe_path, "r") as f:
        content = f.read()
    return {"filename": filename, "content": content}

@app.get("/files/list")
async def list_files_endpoint():
    files = os.listdir(WORKSPACE_DIR)
    return {"files": files}