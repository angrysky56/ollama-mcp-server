#!/usr/bin/env python
"""
Test script to check if prompts are being registered correctly.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ollama_mcp_server.server import mcp

async def test_prompts():
    """Test if prompts are registered."""
    print("Testing Ollama MCP Server prompts...")
    
    # Check if our prompts are registered
    print(f"Server name: {mcp.name}")
    
    # Print out server capabilities
    print(f"Number of tools: {len(mcp._tool_handlers)}")
    print(f"Number of prompts: {len(mcp._prompt_handlers)}")
    
    # List all registered prompts
    print("\nRegistered prompts:")
    for prompt_name in mcp._prompt_handlers.keys():
        print(f"  - {prompt_name}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_prompts())
