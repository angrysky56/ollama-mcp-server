#!/usr/bin/env python
"""
Basic Fast-Agent example: promptwright_coordinator
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Promptwright_Coordinator Agent")

@fast.agent(
    name="promptwright_coordinator_agent",
    instruction="You are a Promptwright dataset generation coordinator. Help users optimize their synthetic dataset generation using local Ollama models like qwen3:14b and deepseek-r1. Provide configuration recommendations, troubleshooting, and workflow optimization.",    model="qwen3:14b",
    servers=[ollama_server]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
