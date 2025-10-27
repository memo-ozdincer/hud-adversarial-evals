"""Tools router for environment interaction."""

from hud.server import MCPRouter
from hud.tools.types import EvaluationResult
from server.shared import http_client
import logging

router = MCPRouter()
logger = logging.getLogger(__name__)

@router.tool
async def act() -> str:
    """Perform one action step in the environment (increment the counter)."""
    try:
        resp = await http_client.post("/act")
        resp.raise_for_status()  # This will raise an error if the request fails (e.g., 4xx or 5xx)
        data = resp.json()
        return f"Action #{data.get('count', 0)} performed. Current count: {data.get('count', 0)}"
    except Exception as e:
        logger.error(f"Error in 'act' tool: {e}")
        return f"Error performing action: {e}" # Ensure a string is always returned

@router.tool
async def setup() -> str:
    """Initialize or reset the environment to its starting state."""
    try:
        await http_client.post("/reset")
        return "Environment reset (counter to 0, workspace cleaned)."
    except Exception as e:
        logger.error(f"Error in 'setup' tool: {e}")
        return f"Error during setup: {e}"

@router.tool
async def evaluate(target: int = 10) -> dict: # <-- CHANGED type hint from EvaluationResult to dict
    """Evaluate progress toward the target count and return a reward and done flag."""
    try:
        resp = await http_client.get("/state")
        resp.raise_for_status()
        current_count = resp.json().get("count", 0)
        delta = target - current_count
        reward = max(0.0, 1.0 - abs(delta) / target) if target > 0 else float(current_count > 0)
        done = current_count >= target

        # Create the result object
        result = EvaluationResult(
            reward=reward,
            done=done,
            content=f"Counter at {current_count}/{target}"
        )
        # Return it as a dictionary for proper serialization
        return result.model_dump() # <-- CHANGED to return a dict
    except Exception as e:
        logger.error(f"Error in 'evaluate' tool: {e}")
        # Return a failure state as a dictionary
        return EvaluationResult(reward=0.0, done=True, content=f"Error during evaluation: {e}").model_dump()