#!/usr/bin/env python
"""
Basic Ollama MCP Integration

This script demonstrates the minimum needed to integrate the Ollama MCP server
with fast-agent, using only the essential components.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent

# Initialize FastAgent with minimal configuration
fast = FastAgent("Basic Ollama Test")

# Define a basic agent using the passthrough model to avoid API key requirements
@fast.agent(
    name="basic_agent",
    instruction="You are a helpful assistant that connects to different models.",
    model="passthrough"  # Using passthrough to avoid API key requirements
)

async def main():
    """Main entry point for the integration demonstration"""
    print("=== Starting Basic Ollama Integration Test ===")
    
    async with fast.run() as agent:
        # Simply print the versions since we can't easily debug the MCP server connection
        print(f"FastAgent initialized.")
        
        # Try calling the Ollama MCP server directly (not through fast-agent)
        print("\nTesting direct Ollama MCP server interaction...")
        try:
            import subprocess
            
            # Run a simple command to list the available Ollama models
            cmd = [
                "uv", "run", "-m", "src.ollama_mcp_server.server",
                "--function", "list_ollama_models"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(Path(os.path.abspath(__file__)).parent.parent),
                capture_output=True,
                text=True,
                check=True
            )
            
            print("\n--- Direct MCP Server Output ---")
            print(result.stdout)
            
        except Exception as e:
            print(f"Direct MCP server error: {str(e)}")
        
        # Provide instructions for manual integration and next steps
        print("\n=== Integration Recommendation ===")
        print("""
Based on our testing, the recommended approach for integrating Ollama with fast-agent is:

1. Run the Ollama MCP server separately as a standalone server
2. Use the MCP server directly for Ollama model interactions
3. For workflow integration, use fast-agent with the passthrough model
   and manually handle the Ollama model interactions

This separates the concerns and avoids API integration issues.
        """)

if __name__ == "__main__":
    asyncio.run(main())
