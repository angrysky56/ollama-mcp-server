#!/usr/bin/env python
"""
Basic Fast-Agent example: dataset_analyzer
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Dataset_Analyzer Agent")

@fast.agent(
    name="dataset_analyzer_agent",
    instruction="You are a synthetic dataset quality analyzer. Review generated datasets from Promptwright, identify patterns, suggest improvements, and help optimize dataset quality for specific use cases like reasoning, coding, or domain expertise.",    model="deepseek-r1:1.5b",
    servers=[ollama_server]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
