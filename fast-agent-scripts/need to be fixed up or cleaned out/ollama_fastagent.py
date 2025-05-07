#!/usr/bin/env python
"""
Ollama Fast-Agent Integration
A standalone script that directly integrates Fast-Agent with the Ollama MCP server
"""

import asyncio
import os
# import sys # unused?
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt
import json
import argparse

# Create command line argument parser
parser = argparse.ArgumentParser(description='Run Fast-Agent with Ollama MCP')
parser.add_argument('--model', type=str, default='phi4-reasoning:plus',
                    help='Ollama model to use (default: phi4-reasoning:plus)')
parser.add_argument('--message', type=str, help='Message to send to the agent')
parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
args = parser.parse_args()

# Set working directory to project root to ensure proper paths
os.chdir(str(Path(__file__).parent))
print(f"Working directory: {os.getcwd()}")

# Create FastAgent instance with direct server configuration
fast = FastAgent("Ollama Agent")

# Define the specific configuration for our server
SERVER_CONFIG = {
    "command": "uv",
    "args": ["run", "-m", "src.server"],
    "cwd": os.getcwd()
}

# Print configuration for debugging
print(f"Using server config: {json.dumps(SERVER_CONFIG, indent=2)}")

@fast.agent(
    name="ollama_agent",
    instruction="You are a helpful assistant that provides clear and insightful responses.",
    model=args.model,
    server_configs={
        "ollama_server": SERVER_CONFIG
    }
)
async def main():
    print("Starting Ollama Agent...")

    try:
        # Run the agent
        async with fast.run() as agent:
            print("Agent started successfully!")

            if args.message:
                print(f"Processing message: {args.message}")
                response = await agent.send(Prompt.user(args.message))
                print("\nAgent Response:")
                print(response.content)
            elif args.interactive:
                print("Starting interactive mode (type 'exit' to quit)...")
                while True:
                    user_input = input("\nYou: ")
                    if user_input.lower() in ('exit', 'quit', 'q'):
                        break

                    response = await agent.send(Prompt.user(user_input))
                    print(f"\nAgent: {response.content}")
            else:
                # Default test message
                print("Sending test message...")
                response = await agent.send(
                    Prompt.user("What are the benefits of using a Model Context Protocol for AI applications?")
                )
                print("\nAgent Response:")
                print(response.content)

    except Exception as e:
        print(f"Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
