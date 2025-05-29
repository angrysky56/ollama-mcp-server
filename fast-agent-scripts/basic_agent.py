#!/usr/bin/env python
"""
Basic Fast-Agent example using Ollama models

This script creates a simple interactive agent that uses your available MCP via fast-agent and Ollama models through the
Ollama MCP server. The agent responds to user input and maintains conversation context.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("basic_agent")

# Define the agent - note that the model is specified at runtime using the --model flag or default is selected from /fastagent.config.yaml
# This way the GUI can specify which Ollama model to use
@fast.agent(
    name="basic_agent",
    instruction="You are a helpful AI assistant with an array of available tools.",
    use_history=True, # Use history to maintain conversation context
    model="gemma-3n-e4b-it",
    # Add the servers defined in fastagent.config.yaml to use for your agent, must use ollama_server for free models.
    servers=[
        "ollama_server",
        "ai-writers-workshop",
        "mcp-logic",
        "arxiv-mcp-server",
        "desktop-commander",
        "brave-search",
        "mcp-code-executor",
        "sqlite",
        "puppeteer"
    ]
)

async def main():
    async with fast.run() as agent:
        # Welcome and instructions
        print("=== Basic Agent Workflow ===")
        print("Tool Use: Practical tool use and information retrieval")
        print("\nSuggested queries to try based on mcp servers if available:")
        print("- Research questions (leverages arxiv-mcp-server or mcp-logic)")
        print("- Write a story (uses ai-writers-workshop)")
        print("- Web content analysis (leverages brave-search tool)")
        print("- System information requests, read/write (leverages desktop-commander)")
        print("- Code execution (leverages mcp-code-executor)")
        print("\nType your query to begin...\n")

        try:
            # For parallel workflows, we use the agent's interactive mode and specify which workflow to use
            await agent.interactive(agent="basic_agent")
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("If you're seeing model-related errors, consider:")
            print("1. Checking if the specified models are available with 'ollama list'")
            print("2. Running with a different model:")


if __name__ == "__main__":
    asyncio.run(main())
