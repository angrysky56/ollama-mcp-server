#!/usr/bin/env python
"""
Chain Workflow Demo using Ollama MCP

This script demonstrates a chain workflow using different Ollama models.
It creates a workflow where:
1. A researcher agent analyzes a topic using phi4-reasoning model
2. A summarizer agent condenses the information using qwen3 model
3. The chain connects these agents in sequence
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Chain Workflow Demo")

@fast.agent(
    name="researcher",
    instruction="You are a thorough researcher who analyzes topics in depth. Provide comprehensive information.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)
@fast.agent(
    name="summarizer",
    instruction="You are a concise summarizer. Take detailed information and create a clear, brief summary.",
    model="qwen3:0.6b",
    servers=["ollama_server"]
)
@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research a topic thoroughly and then summarize the findings concisely."
)
async def main():
    # Run the agent with the chain workflow
    async with fast.run() as agent:
        # Start interactive mode with the research_workflow chain
        await agent.interactive(agent="research_workflow")

if __name__ == "__main__":
    asyncio.run(main())
