#!/usr/bin/env python
"""
Test script for Fast-Agent with Ollama MCP integration
"""

import asyncio
import os
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Set working directory to ensure proper paths
os.chdir("/home/ty/Repositories/ai_workspace/ollama-mcp-server")

# Initialize FastAgent
fast = FastAgent("Test Agent")

# Manually define server config rather than relying on external config file
fast.add_server(
    name="ollama_server",
    config={
        "command": "uv",
        "args": ["run", "-m", "ollama_mcp_server.server"]
    }
)

@fast.agent(
    name="test_agent",
    instruction="You are a helpful AI assistant that analyzes problems step-by-step.",
    model="phi4-reasoning:plus",
    servers=["ollama_server"]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        print("Agent started successfully!")
        
        # Test with a simple message
        response = await agent.send(
            Prompt.user("What are the key benefits of quantum computing?")
        )
        
        print("\nAgent Response:")
        print(response.content)
        
        print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
