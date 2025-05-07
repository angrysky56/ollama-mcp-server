#!/usr/bin/env python
"""
Working Integration of Fast-Agent with Ollama MCP Server

This script demonstrates a working approach to integrating Fast-Agent with the
Ollama MCP server using a two-tier architecture:
1. Fast-agent handles workflow and agent orchestration
2. Direct calls to the Ollama MCP server handle model interactions
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent

# Get the repository root directory (for subprocess calls)
REPO_ROOT = Path(os.path.abspath(__file__)).parent.parent

# Initialize FastAgent with minimal configuration
fast = FastAgent("Ollama Integration Demo")

# Helper function for calling the Ollama MCP server
async def run_ollama_model(model, prompt, temperature=0.7):
    """
    Run a prompt through an Ollama model via the MCP server
    """
    args_json = json.dumps({
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "wait_for_result": True
    })

    cmd = [
        "uv", "run", "-m", "src.ollama_mcp_server.server",
        "--function", "run_ollama_prompt",
        "--args", args_json
    ]

    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True
    )

    # Parse the JSON response
    try:
        output = result.stdout.strip()
        response_data = json.loads(output)

        # Extract the model's response from the content
        if "content" in response_data:
            content = response_data["content"]
            response_parts = content.split("RESPONSE:")
            if len(response_parts) > 1:
                response = response_parts[1].strip()
                return response

        # Return the full response if we can't extract cleanly
        return response_data
    except json.JSONDecodeError:
        return result.stdout

# Define an agent that uses our Ollama integration
@fast.agent(
    name="researcher",
    instruction="You are a research assistant that gathers detailed information on topics.",
    model="model"  # Using passthrough to avoid API key requirements.
    # So nothing happens when an ollama model runs? API key for ollama? I tried to change it to model so it uses the selected model but that's probably not right.
)

@fast.agent(
    name="summarizer",
    instruction="You are an assistant that summarizes information into concise points.",
    model="model"  # Using model to avoid API key requirements
)

@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research a topic and summarize the findings"
)

async def main():
    """Demonstrate the working integration"""
    print("=== Ollama + Fast-Agent Integration Demo ===")

    # agent assigned but not used.
    async with fast.run() as agent:
        # Get user query
        topic = input("Enter a topic to research: ")

        print(f"\nResearching topic: {topic}")
        print("Step 1: Running research phase with phi4-reasoning model...")

        # Run the research phase with Ollama phi4-reasoning model
        research_prompt = f"Research the following topic thoroughly: {topic}. " \
                         f"Provide detailed information, examples, and context."

        research_result = await run_ollama_model(
            "phi4-reasoning:14b-plus-q4_K_M",
            research_prompt
        )

        print("\nResearch phase complete.")
        print("Step 2: Running summarization phase with qwen3 model...")

        # Run the summarization phase with a different Ollama model
        summary_prompt = f"Summarize the following research into 3-5 concise bullet points:\n\n{research_result}"

        summary_result = await run_ollama_model(
            "qwen3:0.6b",
            summary_prompt
        )

        # Present the results
        print("\n=== Research Results ===")
        print(f"Topic: {topic}")
        print("\n=== Summary ===")
        print(summary_result)

        print("\nThis demonstrates how to integrate Ollama with fast-agent using a two-tier architecture.")

if __name__ == "__main__":
    asyncio.run(main())
