#!/usr/bin/env python
"""
Test script to verify the ANSI escape sequence cleaning in the Ollama MCP server.
"""

import asyncio
import re
import json
import sys
import os

# Add the src directory to the path so we can import the server module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ollama_mcp_server.server import run_ollama_prompt, get_job_status


async def test_clean_output():
    """Test that the output from an Ollama model is cleaned of ANSI codes."""
    print("Testing clean output from Ollama models...")
    
    # Run a simple prompt
    model = "cogito:latest"
    prompt = "What is the capital of France?"
    
    print(f"Running prompt with model {model}...")
    result = await run_ollama_prompt(
        model=model,
        prompt=prompt,
        temperature=0.7,
        wait_for_result=True
    )
    
    print("Checking result status...")
    if result["status"] != "complete":
        print(f"ERROR: Prompt execution failed with status {result['status']}")
        return False
    
    # Verify that the content is cleaned
    content = result["content"]
    
    # Define a regex pattern to match ANSI escape sequences
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Check if there are any ANSI escape sequences in the content
    ansi_matches = ansi_pattern.findall(content)
    
    if ansi_matches:
        print(f"ERROR: Found {len(ansi_matches)} ANSI escape sequences in the output")
        print("First few matches:", ansi_matches[:5])
        return False
    
    # Check that the output contains the expected response
    if "RESPONSE:" not in content:
        print("ERROR: Output does not contain 'RESPONSE:' marker")
        return False
    
    response_part = content.split("RESPONSE:", 1)[1].strip()
    print("\nResponse content (first 100 chars):")
    print(response_part[:100])
    
    if "Paris" not in response_part:
        print("ERROR: Response does not contain the expected answer 'Paris'")
        return False
    
    print("Success! Output is clean and contains the expected response.")
    return True


if __name__ == "__main__":
    asyncio.run(test_clean_output())
