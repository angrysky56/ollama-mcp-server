# Ollama MCP Server with [fast-agent](https://fast-agent.ai/#getting-started)

## Currently Claude can probably use ollama features but not agents.

I am working on a hybrid gui approach, claude writes the agent files and the user can run them via gui, fast-agent gui is mostly broken currently. You can use MCP with your local Ollama models this way though, which is cool to me lol.

![alt text](image.png)

You can run this with an activated venv.
You will have to add your own mcp servers AND local model to:

fastagent.config.yaml

and

basic_agent.py

It can run openAI api models too.

# Model configuration (api fees if api key is set in os environment variables)

i.e. Pay: default_model: "openai.gpt-4o"

or

Use a local tool using ollama LLM Free: default_model: "generic.qwen3:30b-a3b"

---

Edit available model and mcp servers here after copying and removing "example_" from file name:

fastagent.config.yaml

And edit the basic agent.py to add your mcp servers you want the agent to use from the config yaml

```python
# In repo root
uv venv
uv pip install -r requirements.txt
```
You can just right-click and run in VS Code or:

```bash
.venv/bin/python
cd fast-agent-scripts
./basic_agent.py
```

A Model Context Protocol (MCP) server that enables Claude to run Ollama models asynchronously, with outputs stored for later retrieval. Built with uv for Python environment management.

## Features

- Run Ollama models without waiting for completion (async)
- Save and manage script templates with variable substitution
- Execute bash commands and multi-step workflows
- All outputs saved to a dedicated directory
- Simple configuration for Claude Desktop


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

1. Copy the content of `claude_desktop_config.json` to your Claude Desktop configuration with your own paths:

```json
{
  "mcpServers": {
     "OllamaMCPServer": {
      "command": "uv",
      "args": [
        "--directory", "/home/ty/Repositories/ai_workspace/ollama-mcp-server/src/ollama_mcp_server",
        "run",
        "server.py"
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
