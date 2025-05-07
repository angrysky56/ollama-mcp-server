#!/usr/bin/env python
"""
Ollama Agent with External Tool Access

This script demonstrates how to create a fast-agent that uses the Ollama MCP server
while also having access to external tools like arxiv.
"""

import asyncio
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Initialize fast-agent
fast = FastAgent("Ollama with Tools")

@fast.agent(
    name="ollama_agent",
    instruction="You are a versatile AI assistant that can use external tools to complete tasks.",
    model="phi4-reasoning:14b-plus-q4_K_M",  # Use Ollama model
    servers=["OllamaMCPServer", "arxiv-mcp-server"]  # Connect to multiple servers
)

async def main():
    """Run the Ollama agent with tools."""
    async with fast.run() as agent:
        # Welcome message
        print("==== Ollama Agent with External Tools ====")
        print("This agent can use multiple MCP servers:")
        print("- OllamaMCPServer for LLM capabilities")
        print("- arxiv-mcp-server for research")
        print("\nYou can ask questions like:")
        print("- 'Find recent papers on quantum computing'")
        print("- 'Explain how transformers work and cite research'")
        print("- 'Write a Python script based on recent ML research'")
        print("\nType 'exit' to quit.")
        print("=========================================\n")
        
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
