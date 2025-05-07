#!/usr/bin/env python
"""
Multi-agent workflow for complex information processing using Ollama models.
This workflow demonstrates research, analysis, and summarization capabilities.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Advanced Workflow")

@fast.agent(
    name="researcher",
    instruction="You research topics thoroughly and provide detailed information with citations. Focus on gathering comprehensive data and exploring different perspectives.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.agent(
    name="analyzer",
    instruction="You analyze information objectively, identify patterns, and provide insightful observations. Focus on critical thinking and detailed examination.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.agent(
    name="summarizer",
    instruction="You synthesize complex information into clear, concise summaries. Focus on extracting key points while maintaining accuracy.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.chain(
    name="research_workflow",
    sequence=["researcher", "analyzer", "summarizer"],
    instruction="Process information through research, analysis, and summarization phases to deliver comprehensive yet concise results."
)

async def main():
    async with fast.run() as agent:
        # Interactive mode for manual testing
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
