#!/usr/bin/env python
"""
Simple script to check Fast-Agent installation and version
"""

import sys
import subprocess
import pkg_resources

print("=== Fast-Agent Version Check ===")

# Check if fast-agent-mcp is installed
try:
    version = pkg_resources.get_distribution("fast-agent-mcp").version
    print(f"fast-agent-mcp version: {version}")
except pkg_resources.DistributionNotFound:
    print("fast-agent-mcp is not installed")

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

print("\n=== Fast-Agent Configuration Check ===")
# Try to find fast-agent configuration file
import os
from pathlib import Path

# Check common locations
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
