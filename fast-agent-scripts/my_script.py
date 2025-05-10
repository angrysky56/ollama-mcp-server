#!/usr/bin/env python
"""
Basic Fast-Agent example: my_script
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent
import os
import sys
from pathlib import Path

# Add the path to the mcp_agent module
# This is necessary to ensure that the module can be imported correctly
# and that the script can find the necessary files.
# This is a workaround for the issue with the module not being found
# when running the script from a different directory.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the path to the mcp_agent module
sys.path.append(str(Path(__file__).resolve().parent.parent / "mcp_agent"))
from mcp_agent.core.fastagent import agent
from mcp_agent.core import OllamaServer
from mcp_agent.core import MCPServer


# Define the server
ollama_server = OllamaServer(
    name="ollama_server",
    host="localhost",
    port=11434,
    # Add any other necessary parameters for the server
)

# Create FastAgent instance
fast = FastAgent("My_Script Agent")

@fast.agent(
    name="my_script_agent",
    instruction="Perform a task",
    use_history=True, # Use history to maintain conversation context
    model="generic.sap3e-aseke-qwen3",
    # Add the servers defined in fastagent.config.yaml to use for your agent, must use ollama_server for free models.
    servers=[
        "ollama_server",
        "arxiv-mcp-server",
        "desktop-commander",
        "brave-search",
        "mcp-code-executor",
        "sqlite",
        "puppeteer"
    ]
    )
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
