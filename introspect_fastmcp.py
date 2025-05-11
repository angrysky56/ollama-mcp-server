#!/usr/bin/env python
"""
Introspect FastMCP to understand its actual structure.
"""

from mcp.server.fastmcp import FastMCP

# Create minimal server
mcp = FastMCP("IntrospectServer")

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
    print("=== FastMCP Introspection ===")
    print(f"Server name: {mcp.name}")
    
    # List all attributes of mcp
    print("\nMCP attributes:")
    for attr in dir(mcp):
        if not attr.startswith('__'):
            print(f"  - {attr}: {type(getattr(mcp, attr))}")
    
    # Check tool manager structure
    if hasattr(mcp, '_tool_manager'):
        print("\nTool manager attributes:")
        tm = mcp._tool_manager
        for attr in dir(tm):
            if not attr.startswith('__'):
                print(f"  - {attr}: {type(getattr(tm, attr))}")
    
    # Check prompt manager structure
    if hasattr(mcp, '_prompt_manager'):
        print("\nPrompt manager attributes:")
        pm = mcp._prompt_manager
        for attr in dir(pm):
            if not attr.startswith('__'):
                print(f"  - {attr}: {type(getattr(pm, attr))}")
    
    print("\n==============================")
