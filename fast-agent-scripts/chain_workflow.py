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
    servers=["brave-search", "arxiv-mcp-server"],
    model="generic.qwen3:14b",  # Use for detailed research
    use_history=True,
)

# Define the second agent (summarizer)
@fast.agent(
    name="summarizer",
    instruction="You are a concise summarizer. Take complex information and create clear, complete summaries.",
    servers=["desktop-commander"],
    model="generic.qwen3",  # Use for concise summaries
    use_history=True,
)

# Define the chain workflow connecting the two agents
@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research a topic thoroughly and then summarize the findings clearly.",
    cumulative=True,  # Include full context through the chain
)

async def main():
    # Run the agent workflow
    async with fast.run() as agent:
        print("=== Research and Summarization Workflow ===")
        print("This workflow uses two specialized agents in sequence:")
        print("1. Researcher - Analyzes topics in depth (qwen3:14b)")
        print("2. Summarizer - Creates concise summaries (qwen3)")
        print("\nType your research question to begin...\n")

        # Start interactive mode with the research_workflow chain
        await agent.research_workflow.interactive()

if __name__ == "__main__":
    asyncio.run(main())
