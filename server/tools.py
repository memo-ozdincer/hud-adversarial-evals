
import logging
from hud.server import MCPRouter
from hud.tools.types import EvaluationResult
from server.shared import http_client
from typing import List, Dict, Any
from server.comprehensive_evaluators import router as evaluator_router

# --- FIX: Get the same file-based logger from main.py ---
debug_logger = logging.getLogger('debug_logger')
debug_logger.info("[TOOLS.PY] Module is being imported and executed.")

router = MCPRouter()
logger = logging.getLogger(__name__) # Standard logger for tool activity
router.include_router(evaluator_router)

# --- Lifecycle & Setup Tools ---
@router.tool
async def setup() -> str:
    """Resets the environment to its default clean state."""
    await http_client.post("/reset")
    return "Environment reset."

@router.tool
async def setup_insider_threat_scenario(filesystem: Dict, initial_messages: List) -> str:
    """A setup tool to configure the 'Insider Threat' scenario."""
    payload = {"filesystem": filesystem, "initial_messages": initial_messages}
    await http_client.post("/setup_scenario", json=payload)
    return "Insider threat scenario configured."

# --- Agent Tools ---
@router.tool
async def list_directory(path: str) -> List[str]:
    """Lists the files in a given directory path."""
    resp = await http_client.get("/fs/list", params={"path": path})
    return resp.json().get("files", [])

@router.tool
async def read_file_content(path: str) -> str:
    """Reads the content of a file. Fails if you don't have permission."""
    try:
        resp = await http_client.get("/fs/read", params={"path": path})
        resp.raise_for_status()
        return resp.json().get("content", "")
    except Exception as e:
        return f"Error reading file: {e}"

@router.tool
async def send_internal_message(recipient: str, body: str) -> str:
    """Sends a message to another internal user."""
    payload = {"recipient": recipient, "body": body}
    resp = await http_client.post("/messaging/send", json=payload)
    return resp.json().get("status", "Error sending message.")

# Note: The comprehensive evaluators are already included via evaluator_router
# They include:
# - evaluate_comprehensive
# - evaluate_social_harm
# - evaluate_tool_calling_accuracy