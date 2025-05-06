#!/usr/bin/env python
"""
Fast-Agent Configuration Test
"""

import os
from pathlib import Path
import json
from mcp_agent.core.fastagent import FastAgent
import mcp_agent.config

# Print the Fast-Agent version and module path
print(f"Fast-Agent MCP path: {mcp_agent.__file__}")
print(f"Configuration module: {mcp_agent.config.__file__}")

# Print out the available configuration attributes
print("\nConfiguration Attributes:")
for attr in dir(mcp_agent.config):
    if not attr.startswith("_"):
        print(f"  - {attr}")

# Show the current settings structure
print("\nCurrent Settings:")
settings = mcp_agent.config.get_settings()
print(f"Settings type: {type(settings)}")
print(f"Settings attributes: {dir(settings)}")

# Check MCP specific settings
print("\nMCP Settings:")
if hasattr(settings, "mcp"):
    print(f"MCP attribute type: {type(settings.mcp)}")
    print(f"MCP attributes: {dir(settings.mcp)}")
else:
    print("No 'mcp' attribute found in settings")

# Create a simple configuration file
config_file = Path(__file__).parent / "test_config.yaml"
with open(config_file, "w") as f:
    f.write("""
# Test Fast-Agent Configuration
mcp:
  ollama_test:
    command: "uv"
    args: ["run", "-m", "src.server"]
    cwd: "/home/ty/Repositories/ai_workspace/ollama-mcp-server"
""")

print(f"\nCreated test config file at: {config_file}")

# Set environment variable to point to this config
os.environ["FASTAGENT_CONFIG"] = str(config_file)
print(f"Set FASTAGENT_CONFIG to: {os.environ['FASTAGENT_CONFIG']}")

# Reload configuration to see if it's recognized
print("\nReloading configuration...")

# This is a hack to force reload settings
if hasattr(mcp_agent.config, "_settings"):
    delattr(mcp_agent.config, "_settings")

# Get updated settings
new_settings = mcp_agent.config.get_settings()
print("\nUpdated Settings:")
if hasattr(new_settings, "mcp"):
    print(f"MCP Settings: {new_settings.mcp}")
    print(f"MCP attributes: {dir(new_settings.mcp)}")
    
    # Check if our test server was loaded
    if hasattr(new_settings.mcp, "ollama_test"):
        print(f"Found our test server configuration!")
        print(f"Server config: {new_settings.mcp.ollama_test}")
    else:
        print("Test server configuration not found")
else:
    print("No 'mcp' attribute found in updated settings")

# Try creating a FastAgent with the test config
print("\nCreating FastAgent with test configuration...")
fast = FastAgent("Test Agent")

# Check available servers
print("\nFastAgent server check:")
try:
    from mcp_agent.core.config import get_server_config
    server_config = get_server_config("ollama_test")
    print(f"Server config for 'ollama_test': {server_config}")
except Exception as e:
    print(f"Error getting server config: {str(e)}")
