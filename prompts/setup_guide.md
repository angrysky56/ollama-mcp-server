# Ollama MCP Server Setup Guide

## Prerequisites

1. **Python 3.8+** with uv package manager
2. **Ollama** installed and running locally
3. **Claude Desktop** for MCP integration

## Installation

### 1. Environment Setup
```bash
cd /home/ty/Repositories/ai_workspace/ollama-mcp-server
uv venv --python 3.12 --seed
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
uv add mcp[cli] python-dotenv
```

### 3. Verify Ollama
```bash
ollama list  # Should show your installed models
ollama serve  # Ensure Ollama is running
```

## Claude Desktop Integration

### 1. Copy Config
Copy the configuration from `example_mcp_config.json` to your Claude Desktop config:

**Linux**: `~/.config/Claude/claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Update Paths
Edit the config to match your system paths:
```json
{
  "mcpServers": {
    "ollama-mcp-server": {
      "command": "uv",
      "args": [
        "--directory", 
        "/YOUR/PATH/TO/ollama-mcp-server",
        "run",
        "python",
        "-m",
        "ollama_mcp_server.server"
      ],
      "env": {
        "OLLAMA_MCP_ROOT": "/YOUR/PATH/TO/ollama-mcp-server"
      }
    }
  }
}
```

### 3. Restart Claude Desktop
Restart Claude Desktop to load the new MCP server.

## Verification

### 1. Check Server Status
In Claude Desktop, you should see the Ollama MCP server tools available.

### 2. Test Basic Function
Try running:
- `list_ollama_models` - Should show your installed models
- `ollama_guide` prompt - Should provide interactive guidance

### 3. Verify Process Management
The server now includes proper cleanup to prevent process leaks:
- Check process count: `ps aux | grep mcp | wc -l` (should be <10)
- Memory usage should remain stable
- No orphaned processes after server shutdown

## Development Mode

For development and testing:

```bash
cd /home/ty/Repositories/ai_workspace/ollama-mcp-server
uv run python -m ollama_mcp_server.server
```

Or use the mcp dev command:
```bash
mcp dev src/ollama_mcp_server/server.py
```

## Directory Structure

```
ollama-mcp-server/
├── src/ollama_mcp_server/
│   └── server.py                 # Main server code
├── outputs/                      # Generated output files
├── scripts/                      # Saved script templates
├── workflows/                    # Workflow definitions
├── fast-agent-scripts/          # Fast-agent Python scripts
├── prompts/                      # Usage guides
├── example_mcp_config.json      # Claude Desktop config example
└── README.md
```

## Environment Variables

Optional environment variables:
- `OLLAMA_MCP_ROOT`: Override base directory path
- Any additional variables for your specific setup

## Troubleshooting

### Common Issues

1. **"Model not found"**
   - Run `ollama list` to see available models
   - Use exact model names from the list

2. **"Connection failed"**
   - Ensure Ollama is running: `ollama serve`
   - Check Ollama is accessible at `http://localhost:11434`

3. **"Server not found in Claude"**
   - Verify config file location
   - Check paths in configuration
   - Restart Claude Desktop

4. **Process/Memory Issues**
   - The server now includes proper cleanup
   - Monitor with: `ps aux | grep mcp`
   - Should see stable process counts

### Logging

Server logs include:
- Process creation/termination
- Job status changes
- Error messages
- Cleanup operations

Check Claude Desktop logs for additional debugging information.

## Features

- ✅ **Process Leak Prevention**: Proper cleanup and signal handling
- ✅ **Async Job Management**: Background task execution
- ✅ **Script Templates**: Reusable prompt templates with variables
- ✅ **Fast-Agent Integration**: Multi-agent workflows
- ✅ **Comprehensive Prompts**: Built-in guidance templates
- ✅ **Error Handling**: Robust error recovery
- ✅ **Output Tracking**: Full job history and results

## Next Steps

1. Explore built-in prompts in Claude Desktop
2. Create your first script template
3. Try multi-agent workflows with fast-agent
4. Monitor system resources to verify leak prevention

The server is now production-ready with proper resource management!
