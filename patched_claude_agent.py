"""Patched ClaudeAgent that respects Anthropic's cache_control limits."""

from hud.agents.claude import ClaudeAgent as BaseClaudeAgent
from anthropic.types import CacheControlEphemeralParam
from anthropic.types.beta import (
    BetaToolParam,
    BetaToolBash20250124Param,
    BetaToolComputerUse20250124Param,
    BetaToolTextEditor20250728Param,
    BetaToolUnionParam,
)
import re
from inspect import cleandoc
import mcp.types as types
from hud.tools.computer.settings import computer_settings


class PatchedClaudeAgent(BaseClaudeAgent):
    """
    Patched ClaudeAgent that limits cache_control blocks to avoid exceeding
    Anthropic's maximum of 4 cache breakpoints.

    This patches the _convert_tools_for_claude method to only add cache_control
    to the first 2 tools (leaving room for message caching which uses 2 more).
    """

    def _convert_tools_for_claude(self) -> None:
        """Convert MCP tools to Claude API tools with limited cache_control."""

        def to_api_tool(tool: types.Tool, add_cache_control: bool = False) -> BetaToolUnionParam:
            cache_control = CacheControlEphemeralParam(type="ephemeral") if add_cache_control else None

            if tool.name == "str_replace_based_edit_tool":
                result = BetaToolTextEditor20250728Param(
                    type="text_editor_20250728",
                    name="str_replace_based_edit_tool",
                )
                if cache_control:
                    result["cache_control"] = cache_control
                return result

            if tool.name == "bash":
                result = BetaToolBash20250124Param(
                    type="bash_20250124",
                    name="bash",
                )
                if cache_control:
                    result["cache_control"] = cache_control
                return result

            if re.fullmatch(self.computer_tool_regex, tool.name):
                result = BetaToolComputerUse20250124Param(
                    type="computer_20250124",
                    name="computer",
                    display_number=1,
                    display_width_px=computer_settings.ANTHROPIC_COMPUTER_WIDTH,
                    display_height_px=computer_settings.ANTHROPIC_COMPUTER_HEIGHT,
                )
                if cache_control:
                    result["cache_control"] = cache_control
                return result

            if tool.description is None or tool.inputSchema is None:
                raise ValueError(
                    cleandoc(f"""MCP tool {tool.name} requires both a description and inputSchema.
                    Add these by:
                    1. Adding a docstring to your @mcp.tool decorated function for the description
                    2. Using pydantic Field() annotations on function parameters for the schema
                    """)
                )

            result = BetaToolParam(
                name=tool.name,
                description=tool.description,
                input_schema=tool.inputSchema,
            )
            if cache_control:
                result["cache_control"] = cache_control
            return result

        self.has_computer_tool = False
        self.tool_mapping = {}
        self.claude_tools = []

        # Only add cache_control to first 2 tools to stay within Anthropic's limit of 4
        # (2 for tools + ~2 for message content blocks)
        tools_with_cache = 0
        max_cached_tools = 2

        for tool in self.get_available_tools():
            add_cache = tools_with_cache < max_cached_tools
            claude_tool = to_api_tool(tool, add_cache_control=add_cache)

            if add_cache:
                tools_with_cache += 1

            # warn if multiple computer tools are found
            if claude_tool["name"] == "computer":
                if self.has_computer_tool:
                    # Silently skip duplicate computer tools
                    continue
                else:
                    self.has_computer_tool = True

            self.tool_mapping[claude_tool["name"]] = tool.name
            self.claude_tools.append(claude_tool)
