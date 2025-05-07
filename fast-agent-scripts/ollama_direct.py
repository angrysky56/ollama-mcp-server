#!/usr/bin/env python
"""
Direct Ollama MCP integration test

This script demonstrates the direct approach to using the Ollama MCP server
without depending on fast-agent's model integrations.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add repository root to Python path for imports
REPO_ROOT = Path(os.path.abspath(__file__)).parent.parent
sys.path.append(str(REPO_ROOT))

from mcp_agent.core.prompt import Prompt

async def main():
    """Test direct Ollama MCP integration"""
    print("=== Testing Direct Ollama MCP Integration ===")
    
    # Directly use the run_ollama_prompt function via subprocess
    import subprocess
    
    # Define a test prompt
    prompt_text = "Explain how Ollama works with MCP in 3 sentences"
    
    # Run the command directly using the Ollama MCP server
    cmd = [
        "uv", "run", "-m", "src.ollama_mcp_server.server", 
        "--function", "run_ollama_prompt",
        "--args", f'{{"model": "qwen3:0.6b", "prompt": "{prompt_text}", "wait_for_result": true}}'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\n=== Result ===")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"\n=== Error ===")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")

if __name__ == "__main__":
    asyncio.run(main())
