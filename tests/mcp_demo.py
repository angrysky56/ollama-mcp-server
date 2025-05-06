#!/usr/bin/env python
"""
Simple Fast-Agent MCP demo for testing Ollama integration
Using the standard Fast-Agent API for version 0.2.21
"""

import asyncio
import os
import sys
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Change to project root directory
os.chdir(str(Path(__file__).parent))
print(f"Working directory: {os.getcwd()}")

# Create a standalone FastAgent instance
fast = FastAgent("MCP Demo")

@fast.agent(
    name="mcp_demo_agent",
    instruction="You are a helpful AI assistant that provides clear and accurate information.",
    model="phi4-reasoning:plus",
    servers=["ollama"]  # Reference to a server we'll define in setup
)
async def main():
    print("Setting up FastAgent with Ollama MCP...")
    
    # Define the Ollama MCP server directly in the FastAgent instance
    # This is the key change from previous approaches
    fast.config.servers["ollama"] = {
        "command": "uv",
        "args": ["run", "-m", "src.server"],
        "cwd": os.getcwd()
    }
    
    print(f"Server configuration: {fast.config.servers}")
    
    try:
        # Run the agent
        async with fast.run() as agent:
            print("Agent started successfully!")
            
            # Test message
            print("Sending test message...")
            response = await agent.send(
                Prompt.user("What are the key principles of quantum computing?")
            )
            
            print("\nResponse from agent:")
            print("-" * 50)
            print(response.content)
            print("-" * 50)
            
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
