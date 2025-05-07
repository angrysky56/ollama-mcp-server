#!/usr/bin/env python
"""
Direct Ollama Test Script

This script demonstrates a direct interaction with Ollama without MCP,
serving as a basic test of connectivity and functionality.
"""

import json
import subprocess
import sys

def run_ollama_prompt(model, prompt, system_prompt=None):
    """Run a prompt directly through Ollama CLI."""
    cmd = ["ollama", "run", model, "--format", "json"]
    
    # Prepare the input JSON
    ollama_input = {
        "prompt": prompt,
        "stream": False  # We don't need streaming for this test
    }
    
    if system_prompt:
        ollama_input["system"] = system_prompt
    
    print(f"Running prompt on {model}...")
    print(f"Prompt: {prompt}")
    
    # Run the command
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the input
    stdout, stderr = process.communicate(input=json.dumps(ollama_input))
    
    if process.returncode != 0:
        print(f"Error: {stderr}")
        return None
    
    # Process output
    try:
        response_data = json.loads(stdout)
        return response_data.get("response", "No response received")
    except json.JSONDecodeError:
        print(f"Error parsing JSON response: {stdout}")
        return None

def main():
    # Use default model or accept from command line
    model = "qwen3:0.6b"
    if len(sys.argv) > 1:
        model = sys.argv[1]
    
    # Get prompt from command line or use default
    prompt = "Explain what makes a good MCP implementation."
    if len(sys.argv) > 2:
        prompt = sys.argv[2]
    
    # Run the test
    result = run_ollama_prompt(
        model=model,
        prompt=prompt,
        system_prompt="You are a helpful technical assistant with knowledge of the Model Context Protocol."
    )
    
    if result:
        print("\nResponse from Ollama:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        print("\nTest completed successfully!")
    else:
        print("\nTest failed. Please check Ollama installation and try again.")

if __name__ == "__main__":
    main()
