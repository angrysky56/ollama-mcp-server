# Ollama MCP Server

A Model Context Protocol (MCP) server that enables Claude to run Ollama models asynchronously, with outputs stored for later retrieval. Built with uv for Python environment management.

## Features

- Run Ollama models without waiting for completion (async)
- Save and manage script templates with variable substitution
- Execute bash commands and multi-step workflows
- All outputs saved to a dedicated directory
- Simple configuration for Claude Desktop

## Project Structure

```
ollama-mcp-server/
├── src/                    # Source code
│   └── server.py           # MCP server implementation
├── outputs/                # Model outputs get stored here
├── scripts/                # Prompt templates and scripts
├── workflows/              # Directory for workflow definitions
├── claude_desktop_config.json  # Claude Desktop configuration
└── README.md
```

## Tools Overview

The server provides these tools to Claude:

### Model Management
- `list_ollama_models`: Lists all locally installed Ollama models

### Prompt Execution
- `run_ollama_prompt`: Run a text prompt through an Ollama model
- `run_script`: Run a script template with variable substitution

### Job Management
- `get_job_status`: Check if a job is completed or still running
- `list_jobs`: View all running and completed jobs
- `cancel_job`: Terminate a running job

### Script Management
- `save_script`: Create a new script template
- `list_scripts`: View available script templates
- `get_script`: Retrieve the content of a saved script

### Bash and Workflow
- `run_bash_command`: Execute shell commands
- `run_workflow`: Run a sequence of steps as a workflow

## Claude Desktop Integration

To use this server with Claude Desktop:

1. Copy the content of `claude_desktop_config.json` to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "OllamaMCPServer": {
      "command": "uv",
      "args": [
        "run",
        "-m",
        "src.server",
        "--directory",
        "/home/ty/Repositories/ai_workspace/ollama-mcp-server"
      ]
    }
  }
}
```

2. Adjust the file paths if needed to match your system

## Usage Examples

### Running a Model

```python
# Run a prompt without waiting for completion
await run_ollama_prompt(
    model="llama3",
    prompt="Explain the concept of quantum entanglement",
    wait_for_result=False
)

# Get the result later
await get_job_status(job_id="job-id-from-previous-response")
```

### Using Script Templates

```python
# Run a template with variable substitution
await run_script(
    script_name="expert_analysis",
    model="llama3",
    variables={
        "domain": "machine learning",
        "content_type": "research paper",
        "topic": "transformer architecture",
        "content": "Paper content goes here..."
    }
)
```

### Running Shell Commands

```python
# Execute a bash command
await run_bash_command(
    command="ollama pull llama3",
    wait_for_result=False
)
```

### Multi-step Workflows

```python
# Execute multiple steps in sequence
await run_workflow(
    steps=[
        {
            "tool": "run_bash_command",
            "params": {
                "command": "ollama pull llama3"
            }
        },
        {
            "tool": "run_ollama_prompt",
            "params": {
                "model": "llama3",
                "prompt": "Explain quantum computing"
            }
        }
    ],
    wait_for_completion=False
)
```
