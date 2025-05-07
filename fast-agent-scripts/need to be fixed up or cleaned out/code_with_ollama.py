#!/usr/bin/env python
"""
Code Execution with Ollama

This script demonstrates a fast-agent that combines:
1. Code execution capabilities from the mcp-code-executor server
2. LLM reasoning from Ollama models
3. File system operations to store and analyze results

The agent can write code, execute it, analyze the results, and improve the code iteratively.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Initialize fast-agent
fast = FastAgent("Code with Ollama")

@fast.agent(
    name="coder",
    instruction="""You are a skilled programmer who can write and execute code to solve problems.
    Write clear, efficient, and well-documented code. Always add error handling and explain your approach.""",
    servers=["mcp-code-executor"]  # Use your existing code executor
)

@fast.agent(
    name="analyzer",
    instruction="""You are a code analyst that can review code execution results and suggest improvements.
    Provide specific, actionable feedback for improving code efficiency, readability, and robustness.""",
    model="phi4-reasoning:14b-plus-q4_K_M",  # Use Ollama model
    servers=["OllamaMCPServer"]
)

@fast.agent(
    name="file_manager",
    instruction="""You help manage code files and execution results. 
    Store files in organized locations with appropriate naming and documentation.""",
    servers=["desktop-commander"]  # Use your existing file system access
)

@fast.chain(
    name="code_and_analyze",
    sequence=["coder", "analyzer"],
    instruction="Write and execute code, then analyze the results."
)

@fast.chain(
    name="complete_workflow",
    sequence=["coder", "file_manager", "analyzer"],
    instruction="""Complete coding workflow:
    1. Write and execute code to solve the problem
    2. Store the code and results in appropriate files
    3. Analyze the code execution and suggest improvements
    """
)

@fast.evaluator_optimizer(
    name="code_optimizer",
    generator="coder",
    evaluator="analyzer",
    min_rating="EXCELLENT",
    max_refinements=3
)

async def main():
    """Run the coding agent workflow."""
    async with fast.run() as agent:
        # Print welcome message
        print("\n" + "="*80)
        print("💻 CODE EXECUTION WITH OLLAMA")
        print("="*80)
        print("\nThis agent combines multiple MCP servers for coding workflows:")
        print("1. 🖥️ Code: Write and execute code (mcp-code-executor)")
        print("2. 🧠 Analysis: Review code with Ollama (OllamaMCPServer)")
        print("3. 📁 Files: Manage code and results (desktop-commander)")
        
        print("\nAvailable workflows:")
        print("- code_and_analyze: Write code and analyze results")
        print("- complete_workflow: Full code-store-analyze pipeline")
        print("- code_optimizer: Iteratively improve code until excellent")
        
        print("\nExample tasks:")
        print("- 'Create a Python script to analyze stock data from a CSV file'")
        print("- 'Write a web scraper to collect information from a website and visualize it'")
        print("- 'Implement a machine learning algorithm to classify text documents'")
        
        print("\nYou can switch between workflows with: @workflow_name")
        print("Type 'exit' to quit the agent.")
        print("="*80 + "\n")
        
        # Start interactive mode with the code optimization workflow
        await agent.interactive(agent="code_optimizer")

if __name__ == "__main__":
    asyncio.run(main())
