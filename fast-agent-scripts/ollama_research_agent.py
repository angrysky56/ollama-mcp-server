#!/usr/bin/env python
"""
Ollama Research Agent

This script demonstrates a fast-agent that can use the Ollama MCP server
for LLM capabilities and the arxiv-mcp-server for research tasks.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Initialize fast-agent
fast = FastAgent("Ollama Research Agent")

@fast.agent(
    name="researcher",
    instruction="You are a research assistant specialized in finding academic papers and extracting information.",
    servers=["arxiv-mcp-server"]  # Use the existing arxiv server
)

@fast.agent(
    name="analyst",
    instruction="You are an AI analyst that can process research findings and provide insights.",
    model="phi4-reasoning:14b-plus-q4_K_M",  # Use Ollama model
    servers=["OllamaMCPServer"]  # Use the Ollama MCP server
)

@fast.chain(
    name="research_workflow",
    sequence=["researcher", "analyst"],
    instruction="Find relevant research papers and analyze their findings."
)

async def main():
    """Run the research agent workflow."""
    async with fast.run() as agent:
        # Print welcome message
        print("\n" + "="*50)
        print("🔍 OLLAMA RESEARCH AGENT")
        print("="*50)
        print("\nThis agent can:")
        print("- Find academic papers via arxiv-mcp-server")
        print("- Analyze findings using Ollama's phi4-reasoning model")
        print("\nExample queries:")
        print("- 'Find recent papers on quantum computing and summarize their findings'")
        print("- 'Research machine learning optimization techniques'")
        print("\nType 'exit' to quit the agent.")
        print("="*50 + "\n")
        
        # Start interactive mode with the research workflow
        await agent.interactive(agent="research_workflow")

if __name__ == "__main__":
    asyncio.run(main())
