#!/usr/bin/env python
"""
Minimal test script to verify FastMCP prompt functionality.
"""

from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("TestPromptServer")

# Add a simple prompt
@mcp.prompt()
async def simple_prompt(message: str) -> str:
    """A simple test prompt"""
    return f"You said: {message}"

# Add a tool for testing
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    print("Starting test server with prompts...")
    mcp.run()
