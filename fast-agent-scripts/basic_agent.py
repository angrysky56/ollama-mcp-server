#!/usr/bin/env python
"""
Basic Fast-Agent example using Ollama models

This script creates a simple interactive agent that uses your available MCP via fast-agent and Ollama models through the
Ollama MCP server. The agent responds to user input and maintains conversation context.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Basic_Agent Agent")

# Define the agent - note that the model is specified at runtime using the --model flag
# This way the GUI can specify which Ollama model to use
@fast.agent(
    name="basic_agent_agent",
    instruction="You are a helpful AI assistant. Respond concisely and accurately to user questions.",
    # Add the servers defined in fastagent.config.yaml to use for your agent, must use ollama_server for free models.
    servers=[
        "ollama_server",
        "arxiv-mcp-server",
        "zonos-tts-mcp",
        "desktop-commander",
        "brave-search",
        "mcp-code-executor"
    ]
)

async def main():
    async with fast.run() as agent:
        # Welcome and instructions
        print("=== Basic Agent Workflow ===")
        print("Tool Use: Practical tool use and information retrieval")
        print("\nSuggested queries to try:")
        print("- Research questions (leverages arxiv-mcp-server)")
        print("- Web content analysis (leverages brave-search tool)")
        print("- System information requests, read/write (leverages desktop-commander)")
        print("- Code execution (leverages mcp-code-executor)")
        print("\nType your query to begin...\n")

        try:
            # For parallel workflows, we use the agent's interactive mode and specify which workflow to use
            await agent.interactive(agent="basic_agent_agent")
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("If you're seeing model-related errors, consider:")
            print("1. Checking if the specified models are available with 'ollama list'")
            print("2. Running with a different model:")


if __name__ == "__main__":
    asyncio.run(main())
