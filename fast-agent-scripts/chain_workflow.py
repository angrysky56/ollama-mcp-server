#!/usr/bin/env python
"""
Chain Workflow Example using Ollama models

This script creates a workflow with two agents in sequence:
1. A researcher agent that gathers information
2. A summarizer agent that creates concise summaries

Both agents use Ollama models through the Ollama MCP server.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Chain Workflow Agent")

# Define the first agent (researcher)
@fast.agent(
    name="researcher",
    instruction="You are a thorough researcher. Analyze topics deeply and provide detailed information.",
    servers=["ollama_server"]
)

# Define the second agent (summarizer)
@fast.agent(
    name="summarizer",
    instruction="You are a concise summarizer. Take complex information and create clear, brief summaries.",
    servers=["ollama_server"]
)

# Define the chain workflow connecting the two agents
@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research a topic thoroughly and then summarize the findings clearly."
)

async def main():
    # Run the agent workflow
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
