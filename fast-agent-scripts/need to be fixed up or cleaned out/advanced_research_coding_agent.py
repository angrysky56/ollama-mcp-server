#!/usr/bin/env python
"""
Advanced Research & Coding Agent

This script demonstrates a sophisticated fast-agent workflow that combines:
1. Research capabilities via arxiv-mcp-server
2. Code execution via mcp-code-executor
3. Data storage via chroma
4. Analysis via Ollama models

The agent can research topics, generate and execute code based on the research,
store results in a vector database, and provide comprehensive analysis.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Initialize fast-agent
fast = FastAgent("Advanced Research & Coding Agent")

# Define various agents that connect to different MCP servers
@fast.agent(
    name="researcher",
    instruction="""You are a research specialist that finds academic papers and extracts key information.
    Always provide paper IDs, titles, authors, and publication dates when reporting findings.
    Summarize the key contributions and methodologies from each paper.""",
    servers=["arxiv-mcp-server"]
)

@fast.agent(
    name="coder",
    instruction="""You are a programming expert that implements algorithms and analyses based on research papers.
    Generate clean, well-documented code with proper error handling.
    Include comments explaining how the implementation relates to the research.""",
    servers=["mcp-code-executor"]
)

@fast.agent(
    name="data_manager",
    instruction="""You are a data management specialist that stores and retrieves information from vector databases.
    Organize information efficiently with appropriate metadata and tagging.""",
    servers=["chroma"]
)

@fast.agent(
    name="analyzer",
    instruction="""You are an analytical expert that evaluates research findings and code results.
    Provide clear, insightful analysis with specific conclusions and recommendations.
    Connect the analysis back to the original research questions.""",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["OllamaMCPServer"]
)

# Define a simple chain for research and analysis
@fast.chain(
    name="research_analysis",
    sequence=["researcher", "analyzer"],
    instruction="Research a topic and analyze the findings."
)

# Define a code implementation chain
@fast.chain(
    name="research_implementation",
    sequence=["researcher", "coder"],
    instruction="Research a topic and implement code based on the findings."
)

# Define a complete research-code-analyze workflow
@fast.chain(
    name="full_workflow",
    sequence=["researcher", "coder", "data_manager", "analyzer"],
    instruction="""Complete end-to-end workflow:
    1. Research the topic to find relevant papers
    2. Generate and execute code based on the research
    3. Store the results and findings in the database
    4. Analyze the overall process and provide insights
    """
)

async def main():
    """Run the advanced agent workflow."""
    async with fast.run() as agent:
        # Print welcome message
        print("\n" + "="*80)
        print("🔬 ADVANCED RESEARCH & CODING AGENT")
        print("="*80)
        print("\nThis agent integrates multiple MCP servers to create a sophisticated workflow:")
        print("1. 📚 Research: Find and analyze academic papers (arxiv-mcp-server)")
        print("2. 💻 Code: Generate and execute code (mcp-code-executor)")
        print("3. 💾 Storage: Store and retrieve data (chroma)")
        print("4. 🧠 Analysis: Evaluate results (OllamaMCPServer with phi4-reasoning)")
        
        print("\nAvailable workflows:")
        print("- research_analysis: Research a topic and analyze findings")
        print("- research_implementation: Research a topic and implement code")
        print("- full_workflow: Complete end-to-end process")
        
        print("\nExample queries:")
        print("- 'Research recent advances in transformer architecture efficiency'")
        print("- 'Implement a BERT-based text classifier based on recent papers'")
        print("- 'Research quantum algorithms and create a quantum circuit simulator'")
        
        print("\nYou can switch between workflows with: @workflow_name")
        print("Type 'exit' to quit the agent.")
        print("="*80 + "\n")
        
        # Start interactive mode with the full workflow
        # You can also specify a different workflow with agent="research_analysis"
        await agent.interactive(agent="full_workflow")

if __name__ == "__main__":
    asyncio.run(main())
