#!/usr/bin/env python
"""
Debug script to understand FastMCP prompt registration.
"""

from mcp.server.fastmcp import FastMCP

# Create minimal server
mcp = FastMCP("DebugServer")

# Add a tool
@mcp.tool()
def test_tool(a: int) -> int:
    """Test tool"""
    return a * 2

# Add a prompt
@mcp.prompt()
async def test_prompt(message: str) -> str:
    """Test prompt"""
    return f"Prompt response: {message}"

if __name__ == "__main__":
    print("=== FastMCP Debug Info ===")
    print(f"Server name: {mcp.name}")
    
    # Check tool registration
    print(f"\nTool manager: {hasattr(mcp, '_tool_manager')}")
    if hasattr(mcp, '_tool_manager'):
        print(f"Tools registered: {len(mcp._tool_manager.tools)}")
        for tool_name, tool in mcp._tool_manager.tools.items():
            print(f"  - {tool_name}: {tool.description}")
    
    # Check prompt registration 
    print(f"\nPrompt manager: {hasattr(mcp, '_prompt_manager')}")
    if hasattr(mcp, '_prompt_manager'):
        print(f"Prompts registered: {len(mcp._prompt_manager.prompts)}")
        for prompt_name, prompt in mcp._prompt_manager.prompts.items():
            print(f"  - {prompt_name}: {prompt.description}")
    
    print("\n=========================")
    
    # Run server
    mcp.run()
