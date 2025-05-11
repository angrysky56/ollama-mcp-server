#!/usr/bin/env python
"""
Verify if prompts are being registered in the main server.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ollama_mcp_server.server import mcp

if __name__ == "__main__":
    print("=== Ollama MCP Server Verification ===")
    print(f"Server name: {mcp.name}")
    
    # Check tool manager
    if hasattr(mcp, '_tool_manager'):
        print(f"\nTools registered: {len(mcp._tool_manager._tools)}")
        for tool_name in mcp._tool_manager._tools.keys():
            print(f"  - {tool_name}")
    
    # Check prompt manager
    if hasattr(mcp, '_prompt_manager'):
        print(f"\nPrompts registered: {len(mcp._prompt_manager._prompts)}")
        for prompt_name in mcp._prompt_manager._prompts.keys():
            print(f"  - {prompt_name}")
    
    print("\n=====================================")
