#!/usr/bin/env python
"""
Embedded configuration Fast-Agent for testing with Ollama MCP
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Import the Fast-Agent modules
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt
import mcp_agent.config as config

# Set working directory to the project root
os.chdir(str(Path(__file__).parent))

# Define the Ollama MCP server configuration directly
OLLAMA_CONFIG = {
    "mcp": {
        "ollama_server": {
            "command": "uv",
            "args": ["run", "-m", "src.server"],
            "cwd": str(Path(__file__).parent)
        }
    }
}

print("Configuring FastAgent with embedded configuration")
print(f"Server config: {json.dumps(OLLAMA_CONFIG['mcp']['ollama_server'], indent=2)}")

# Set the configuration programmatically
config.CONFIG = OLLAMA_CONFIG

# Create the FastAgent instance
fast = FastAgent("Embedded Agent")

@fast.agent(
    name="embedded_agent",
    instruction="You are a helpful assistant that provides concise and informative responses.",
    model="phi4-reasoning:plus",
    servers=["ollama_server"]
)
async def main():
    # Print debug information
    print("Starting Embedded Agent...")
    print(f"Current directory: {os.getcwd()}")

    try:
        # Run the agent
        async with fast.run() as agent:
            print("Agent started successfully!")

            # Process command line arguments
            if len(sys.argv) > 1:
                # Get the message from command line
                message = " ".join(sys.argv[1:])
                print(f"Processing message: {message}")

                # Send the message to the agent
                response = await agent.send(Prompt.user(message))

                # Print the response
                print("\nAgent Response:")
                print(response.content)
            else:
                # Send a test message
                print("Sending test message...")
                response = await agent.send(Prompt.user("What are the top 3 benefits of quantum computing?"))

                # Print the response
                print("\nAgent Response:")
                print(response.content)

    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
