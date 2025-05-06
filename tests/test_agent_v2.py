#!/usr/bin/env python
"""
Test script for Fast-Agent v0.2.21 with Ollama MCP integration
"""

import asyncio
import os
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt
import mcp_agent.config as config

# Set working directory
os.chdir("/home/ty/Repositories/ai_workspace/ollama-mcp-server")

# Create a runtime configuration directly
runtime_config = {
    "mcp": {
        "ollama_server": {
            "command": "uv",
            "args": ["run", "-m", "src.server"],
            "cwd": "/home/ty/Repositories/ai_workspace/ollama-mcp-server"
        }
    }
}

# Update the config at runtime
config.set_runtime_config(runtime_config)

# Create FastAgent instance
fast = FastAgent("Test Agent")

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
