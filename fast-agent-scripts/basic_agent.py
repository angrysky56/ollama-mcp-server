#!/usr/bin/env python
"""
Basic Fast-Agent example: basic_agent
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Basic_Agent Agent")

@fast.agent(
    name="basic_agent_agent",
    instruction="You are a helpful AI agent that specializes in graph reasoning and knowledge representation.",
    servers=["ollama_server"]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
