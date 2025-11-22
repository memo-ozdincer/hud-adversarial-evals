#!/usr/bin/env python
"""
Test script to verify the priority-based caching fix works with hud eval.
Run with: python test_patched_agent.py
"""

from __future__ import annotations

import asyncio
import json

from patched_claude_agent import PatchedClaudeAgent
from hud.datasets import Task


async def main():
    """Run a single task with the patched agent to test cache_control fix."""

    # Load the first task from tasks.json
    with open("tasks.json") as f:
        tasks_data = json.load(f)

    if not tasks_data:
        print("❌ No tasks found in tasks.json")
        return

    task_data = tasks_data[0]
    task = Task(**task_data)

    print(f"🧪 Testing patched agent with task: {task.id}")
    print(f"   Using priority-based cache allocation")
    print(f"   Priority tools: {PatchedClaudeAgent.PRIORITY_TOOLS}")
    print(f"   Max cached tools: {PatchedClaudeAgent.MAX_TOOL_CACHE_BREAKPOINTS}")
    print()

    # Initialize the patched agent with the task
    agent = PatchedClaudeAgent()
    await agent.initialize(task)

    try:
        # Run the task with the patched agent
        result = await agent.run(
            prompt_or_task=task,
            max_steps=10,
        )

        print(f"\n✅ Task completed successfully!")
        print(f"   Reward: {result.reward}")
        print(f"   Total steps: {len(result.steps)}")
        if result.evaluation_result:
            print(f"   Evaluation: {result.evaluation_result}")

    except Exception as e:
        if "cache_control" in str(e).lower():
            print(f"\n❌ Cache control error still occurring:")
            print(f"   {e}")
            print(f"\n   The fix may need adjustment.")
        else:
            print(f"\n❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
