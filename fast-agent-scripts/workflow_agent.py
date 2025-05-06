#!/usr/bin/env python
"""
Workflow Fast-Agent example using Ollama MCP Server.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Ollama Workflow Agent")

@fast.agent(
    name="researcher",
    instruction="You research topics thoroughly and provide detailed information.",
    servers=["ollama_server"]
)

@fast.agent(
    name="summarizer",
    instruction="You take complex information and summarize it concisely.",
    servers=["ollama_server"]
)

@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research and summarize information effectively"
)

async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
