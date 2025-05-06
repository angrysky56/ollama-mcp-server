#!/usr/bin/env python
"""
Test script for Fast-Agent v0.2.21 with Ollama MCP integration
Using the CLI approach and environment variables for configuration
"""

import asyncio
import os
import sys
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Set configuration using environment variables
os.environ["FASTAGENT_CONFIG"] = str(Path(__file__).parent / ".fastagent" / "config.yaml")

# Create fast-agent configuration directory if it doesn't exist
config_dir = Path(__file__).parent / ".fastagent"
config_dir.mkdir(exist_ok=True)

# Write configuration file
config_path = config_dir / "config.yaml"
with open(config_path, "w") as f:
    f.write("""
# Fast-Agent Configuration File
mcp:
  ollama_server:
    command: "uv"
    args: ["run", "-m", "src.server"]
    cwd: "/home/ty/Repositories/ai_workspace/ollama-mcp-server"
    """)

print(f"Configuration file written to: {config_path}")

# Create FastAgent instance
fast = FastAgent("Test Agent")

@fast.agent(
    name="test_agent",
    instruction="You are a helpful AI assistant that analyzes problems step-by-step.",
    model="phi4-reasoning:plus",
    servers=["ollama_server"]
)
async def main():
    try:
        # Run the agent
        async with fast.run() as agent:
            print("Agent started successfully!")
            
            # Test with a simple message
            print("Sending test message to agent...")
            response = await agent.send(
                Prompt.user("What are the key benefits of quantum computing?")
            )
            
            print("\nAgent Response:")
            print(response.content)
            
            print("\nTest completed successfully!")
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
