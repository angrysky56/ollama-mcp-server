#!/usr/bin/env python
"""
Workflow Fast-Agent example: research_summary_agent
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Research_Summary_Agent Agent")

@fast.agent(
    name="researcher",
    instruction="You research topics thoroughly and provide detailed information.",
    servers=[ollama_server]
)

@fast.agent(
    name="summarizer",
    instruction="You take complex information and summarize it concisely.",
    servers=[ollama_server]
)

@fast.chain(
    name="research_summary_agent_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Find the latest research papers on a topic and summarize their key findings. Steps: 1. Search academic databases (e.g., Google Scholar, arXiv) for recent papers. 2. Extract abstracts and key findings. 3. Generate concise summaries. 4. Prioritize papers by relevance and citations."
)

async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
