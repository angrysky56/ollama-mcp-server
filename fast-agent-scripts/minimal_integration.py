#!/usr/bin/env python
"""
Minimal Integration Test for Ollama MCP + Fast-Agent

This script demonstrates how to integrate Ollama with Fast-Agent using the
MCP server approach. It implements a simplified workflow that handles
interaction with Ollama models through the MCP server.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent
from mcp.types import PromptMessage, TextContent

# Create FastAgent instance with minimal configuration
fast = FastAgent("Minimal Integration Test")

@fast.agent(
    name="mcp_agent",
    instruction="You are a helpful assistant that connects to the Ollama MCP server.",
    servers=["ollama_server"]
)
async def main():
    """Main function to demonstrate the integration"""
    print("=== Starting Minimal Integration Test ===")
    
    async with fast.run() as agent:
        print("Agent initialized, setting up MCP server connection...")
        
        # Define a test prompt
        prompt_text = "Explain how Ollama works with MCP in 3 sentences"
        print(f"Test prompt: {prompt_text}")
        
        try:
            # Call the Ollama MCP server tool directly
            result = await agent.ollama_server.run_ollama_prompt(
                model="qwen3:0.6b",
                prompt=prompt_text,
                wait_for_result=True
            )
            
            print("\n=== Result from Ollama MCP Server ===")
            if isinstance(result, dict) and "content" in result:
                # Extract and display the model response
                content = result["content"]
                
                # Find and display the model's response
                response_parts = content.split("RESPONSE:")
                if len(response_parts) > 1:
                    response = response_parts[1].strip()
                    print("Model response:")
                    print(response)
                else:
                    print("Full content:")
                    print(content)
            else:
                print("Unexpected result format:")
                print(result)
            
        except Exception as e:
            print(f"\n=== Error ===\n{str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
