#!/usr/bin/env python
"""
Basic Fast-Agent example: demo_fix
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Demo_Fix Agent")

@fast.agent(
    name="demo_fix_agent",
    instruction="You are a helpful assistant focused on explanations about MCP servers.",
    model="qwen3:0.6b",
    servers=["ollama_server"]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
