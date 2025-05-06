#!/usr/bin/env python
"""
Simple script to check Fast-Agent installation and version
"""

import sys
import subprocess
import os
from pathlib import Path

print("=== Fast-Agent Version Check ===")

# Try to run fast-agent CLI command to check version
try:
    result = subprocess.run(
        ["fast-agent", "--version"], 
        capture_output=True, 
        text=True,
        check=False
    )
    print(f"fast-agent CLI version output: {result.stdout.strip()}")
    print(f"fast-agent CLI error (if any): {result.stderr.strip()}")
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error running fast-agent CLI: {e}")

# Try to get help output
try:
    result = subprocess.run(
        ["fast-agent", "check", "--help"], 
        capture_output=True, 
        text=True,
        check=False
    )
    print(f"\nfast-agent check help output: {result.stdout.strip()}")
except Exception as e:
    print(f"Error getting fast-agent check help: {e}")

print("\n=== Python Path ===")
for path in sys.path:
    print(path)

print("\n=== Python Environment ===")
try:
    result = subprocess.run(
        ["pip", "list"], 
        capture_output=True, 
        text=True,
        check=False
    )
    print(f"Installed packages: {result.stdout.strip()}")
except Exception as e:
    print(f"Error getting pip list: {e}")

print("\n=== Fast-Agent Configuration Check ===")
# Try to find fast-agent configuration file
locations = [
    Path.cwd() / "fastagent.config.yaml",
    Path.cwd() / ".fastagent" / "config.yaml",
    Path.home() / ".fastagent" / "config.yaml",
    Path("/home/ty/Repositories/ai_workspace/ollama-mcp-server/src/fast-agent-scripts/fastagent.config.yaml")
]

for location in locations:
    if location.exists():
        print(f"Found configuration file at: {location}")
        try:
            with open(location, "r") as f:
                content = f.read()
                print(f"Content: {content[:200]}...")
        except Exception as e:
            print(f"Error reading config: {e}")
    else:
        print(f"No configuration file at: {location}")

# Check if mcp_agent module is available
print("\n=== MCP Agent Module Check ===")
try:
    import mcp_agent
    print(f"mcp_agent module found: {mcp_agent.__file__}")
    
    # Try to import Fast-Agent
    from mcp_agent.core.fastagent import FastAgent
    print("FastAgent class imported successfully")
    
    # Check available config attributes
    import mcp_agent.config
    print(f"mcp_agent.config attributes: {dir(mcp_agent.config)}")
    
except ImportError as e:
    print(f"Error importing mcp_agent: {e}")
except Exception as e:
    print(f"Other error: {e}")
