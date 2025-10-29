### Final Corrected server/main.py

import logging
import sys
import asyncio
import os
import uuid # Import the UUID library
from hud.server import MCPServer
from server.shared import http_client

run_id = str(uuid.uuid4())
os.environ['HUD_RUN_ID'] = run_id
output_dir = f"/output/{run_id}"

debug_logger = logging.getLogger('debug_logger')
debug_logger.setLevel(logging.INFO)

os.makedirs(output_dir, exist_ok=True)
file_handler = logging.FileHandler(f'{output_dir}/debug.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
debug_logger.addHandler(file_handler)
debug_logger.info(f"[MAIN.PY] SCRIPT EXECUTION STARTED. Run ID: {run_id}")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    force=True,
)

backend_process = None
mcp = MCPServer(name="test0-environment-v2")

from server.tools import router as tools_router
mcp.include_router(tools_router)

@mcp.initialize
async def init():
    global backend_process
    debug_logger.info("[MAIN.PY] MCP INITIALIZE hook running.")
    if backend_process is None:
        debug_logger.info("[MAIN.PY] Starting Uvicorn backend server...")
        backend_process = await asyncio.create_subprocess_shell(
            "uvicorn server.backend:app --host 0.0.0.0 --port $ENV_SERVER_PORT --log-level warning",
        )
        await asyncio.sleep(2)
        debug_logger.info("[MAIN.PY] Uvicorn backend server should be running.")
    await http_client.get("/health")


@mcp.shutdown
async def cleanup():
    global backend_process
    debug_logger.info("[MAIN.PY] MCP SHUTDOWN hook running.")
    await http_client.aclose()
    if backend_process:
        debug_logger.info("[MAIN.PY] Terminating Uvicorn backend server...")
        backend_process.terminate()
        await backend_process.wait()
        debug_logger.info("[MAIN.PY] Uvicorn backend server terminated.")
        backend_process = None


if __name__ == "__main__":
    debug_logger.info("[MAIN.PY] Starting MCP server run loop.")
    mcp.run(transport="stdio")
    debug_logger.info("[MAIN.PY] MCP server run loop finished.")