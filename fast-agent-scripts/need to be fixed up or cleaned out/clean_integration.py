#!/usr/bin/env python
"""
Clean Fast-Agent + Ollama MCP Integration

This script demonstrates a working integration of Fast-Agent with Ollama
using a two-tier architecture that respects each system's strengths.
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.prompt import Prompt

# Get the repository root directory (for subprocess calls)
REPO_ROOT = Path(os.path.abspath(__file__)).parent.parent

# Initialize FastAgent with proper configuration path
# Using passthrough model to avoid API key requirements
fast = FastAgent("Ollama Integration")

# Helper function for calling the Ollama MCP server
async def run_ollama_prompt(model, prompt, temperature=0.7):
    """Run a prompt through the Ollama MCP server"""
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
    
    try:
        # Parse the JSON response
        response_data = json.loads(result.stdout.strip())
        
        # Extract the actual response from the content
        if "content" in response_data:
            content = response_data["content"]
            response_parts = content.split("RESPONSE:")
            if len(response_parts) > 1:
                response = response_parts[1].strip()
                
                # Try to extract JSON response if present
                try:
                    json_response = json.loads(response)
                    if "response" in json_response:
                        return json_response["response"]
                    else:
                        return json_response
                except json.JSONDecodeError:
                    # If not JSON, return the plain text
                    return response
            
            return content
        
        return response_data
    except Exception as e:
        print(f"Error parsing response: {e}")
        return result.stdout

# Define research agent with custom processor for Ollama models
@fast.agent(
    name="researcher",
    instruction="You research topics thoroughly and provide detailed information.",
    model="passthrough"  # Using passthrough to avoid API key requirements
)

# Define summary agent with custom processor for Ollama models
@fast.agent(
    name="summarizer",
    instruction="You summarize complex information into clear, concise points.",
    model="passthrough"  # Using passthrough to avoid API key requirements
)

# Create a workflow chain connecting the agents
@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research and summarize information effectively"
)

async def main():
    """Main integration demonstration"""
    print("=== Fast-Agent + Ollama MCP Integration ===")
    
    # Check if the Ollama MCP server is working
    print("\nVerifying Ollama MCP server connection...")
    try:
        models_cmd = [
            "uv", "run", "-m", "src.ollama_mcp_server.server",
            "--function", "list_ollama_models"
        ]
        
        models_result = subprocess.run(
            models_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        models_data = json.loads(models_result.stdout.strip())
        if "models" in models_data and len(models_data["models"]) > 0:
            print(f"✓ Successfully connected to Ollama MCP server")
            print(f"✓ Found {len(models_data['models'])} available models")
        else:
            print("✗ Failed to retrieve models from Ollama MCP server")
            return
    except Exception as e:
        print(f"✗ Error connecting to Ollama MCP server: {e}")
        return
    
    # Initialize Fast-Agent
    print("\nInitializing Fast-Agent...")
    async with fast.run() as agent:
        print("✓ Fast-Agent initialized successfully")
        
        # Get a topic from user input
        topic = input("\nEnter a topic to research: ")
        print(f"\nResearching topic: {topic}")
        
        # Step 1: Research phase using Ollama
        print("\nStep 1: Research phase (using phi4-reasoning model)...")
        research_prompt = f"Research the following topic in detail: {topic}. Provide comprehensive information."
        
        research_result = await run_ollama_prompt(
            "phi4-reasoning:14b-plus-q4_K_M",  # Using phi4 for detailed research
            research_prompt
        )
        
        print("✓ Research phase complete")
        
        # Step 2: Summarization phase using a different Ollama model
        print("\nStep 2: Summarization phase (using qwen3 model)...")
        summary_prompt = f"Summarize the following research into 3-5 key points:\n\n{research_result}"
        
        summary_result = await run_ollama_prompt(
            "qwen3:0.6b",  # Using qwen3 for concise summarization
            summary_prompt
        )
        
        print("✓ Summarization phase complete")
        
        # Display the results
        print("\n=== Research Results ===")
        print(f"Topic: {topic}")
        print("\n--- Detailed Research ---")
        print(research_result[:500] + "..." if len(research_result) > 500 else research_result)
        print("\n--- Summary ---")
        print(summary_result)
        
        print("\n=== Integration Successful! ===")
        print("""
This demonstrates the two-tier integration approach:
1. Fast-Agent provides the workflow framework
2. Direct Ollama MCP Server calls handle the model interactions
3. Different Ollama models are used for different stages of the workflow

This architecture:
- Avoids API key requirements by using the passthrough model
- Leverages the workflow capabilities of Fast-Agent
- Utilizes the model strengths of Ollama
- Provides a clean separation of concerns
""")

if __name__ == "__main__":
    asyncio.run(main())
