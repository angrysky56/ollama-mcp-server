#!/usr/bin/env python
"""
Demo Agent for testing Fast-Agent with Ollama MCP integration
"""

import asyncio
import os
import sys
from pathlib import Path
# Import the Fast-Agent modules
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt


# Add the necessary paths to find modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent
project_dir = src_dir.parent

# Add project directory to sys.path if needed
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Set environment variable to point to the correct config file
os.environ["FASTAGENT_CONFIG"] = str(current_dir / "fastagent.config.yaml")
print(f"Using config file: {os.environ['FASTAGENT_CONFIG']}")

# Create the FastAgent instance
fast = FastAgent("Demo Agent")

@fast.agent(
    name="demo_agent",
    instruction="You are a helpful assistant that provides concise and informative responses.",
    model="phi4-reasoning:plus",
    servers=["ollama_server"]
)
async def main():
    # Print debug information
    print("Starting Demo Agent...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Config file location: {os.environ.get('FASTAGENT_CONFIG')}")

    try:
        # Run the agent
        async with fast.run() as agent:
            print("Agent started successfully!")

            if len(sys.argv) > 1 and sys.argv[1] == "--message" and len(sys.argv) > 2:
                # Process message from command line
                message = sys.argv[2]
                print(f"Processing message: {message}")

                # Send the message to the agent
                response = await agent.send(Prompt.user(message))

                # Print the response
                print("\nAgent Response:")
                print(response.content)
            else:
                # Start interactive mode
                print("Starting interactive mode...")
                await agent.interactive()

    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
