#!/usr/bin/env python
"""
Basic Fast-Agent example using Ollama models

This script creates a simple interactive agent that uses Ollama models through the
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
        "desktop-commander"
    ]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
