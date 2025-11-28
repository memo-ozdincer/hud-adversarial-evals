import sys
import logging
from hud.server import MCPServer
from shared import http_client

# Configure logging to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    force=True,
)
for logger_name in ["httpx", "httpcore"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Create main MCP server
mcp = MCPServer(name="test0-environment")

# Include routers and mount hubs
from tools import router as tools_router, setup_hub, evaluate_hub

mcp.include_router(tools_router)

# Mount lifecycle hubs (hidden from agents)
mcp.mount(setup_hub)
mcp.mount(evaluate_hub)


# Lifecycle hooks
@mcp.initialize
async def init():
    """Check if the environment is healthy with retry logic"""
    import asyncio

    if not http_client:
        raise ValueError("http_client is not set")

    # Retry health check with exponential backoff
    max_retries = 10
    for attempt in range(max_retries):
        try:
            await http_client.get("/health")
            logging.info(f"Backend health check passed on attempt {attempt + 1}")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 0.5 * (2 ** attempt)  # Exponential backoff: 0.5s, 1s, 2s, 4s...
                logging.warning(f"Backend not ready (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            else:
                logging.error(f"Backend failed to start after {max_retries} attempts")
                raise


@mcp.shutdown
async def cleanup():
    """Close the HTTP client"""
    if http_client:
        await http_client.aclose()


if __name__ == "__main__":
    mcp.run(transport="stdio")
