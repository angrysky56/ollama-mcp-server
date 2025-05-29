# Ollama MCP Server

A comprehensive Model Context Protocol (MCP) server for Ollama integration with advanced features including script management, multi-agent workflows, and process leak prevention.

## 🌟 Features

- **🔄 Async Job Management**: Execute long-running tasks in the background
- **📝 Script Templates**: Create reusable prompt templates with variable substitution
- **🤖 Fast-Agent Integration**: Multi-agent workflows (chain, parallel, router, evaluator)
- **🛡️ Process Leak Prevention**: Proper cleanup and resource management
- **📊 Comprehensive Monitoring**: Job tracking, status monitoring, and output management
- **🎯 Built-in Prompts**: Interactive guidance templates for common tasks
- **⚡ Multiple Model Support**: Work with any locally installed Ollama model

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with [uv](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.ai/) installed and running
- [Claude Desktop](https://claude.ai/download) for MCP integration

### Installation

1. **Setup Environment**:
Be advised- This readme was revised by a less than concientious AI.

```bash
cd /path/to/ollama-mcp-server
uv venv --python 3.12 --seed
source .venv/bin/activate
uv add mcp[cli] python-dotenv
```

2. **Configure Claude Desktop**:
Copy configuration from `example_of_bad_ai_gen_mcp_config_do_not_use.json` (Don't lol. Use the example_claude_desktop_config.json)to your Claude Desktop config file:
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Update paths** in the config to match your system

4. **Restart Claude Desktop**

## 🛠️ Available Tools

### Core Operations
- `list_ollama_models` - Show all available Ollama models
- `run_ollama_prompt` - Execute prompts with any model (sync/async)
- `get_job_status` - Check job completion status
- `list_jobs` - View all running and completed jobs
- `cancel_job` - Stop running jobs

### Script Management
- `save_script` - Create reusable prompt templates
- `list_scripts` - View saved templates
- `get_script` - Read template content
- `run_script` - Execute templates with variables

### Fast-Agent Workflows
- `create_fastagent_script` - Single-agent scripts
- `create_fastagent_workflow` - Multi-agent workflows
- `run_fastagent_script` - Execute agent workflows
- `list_fastagent_scripts` - View available workflows

### System Integration
- `run_bash_command` - Execute system commands safely
- `run_workflow` - Multi-step workflow execution

## 📖 Built-in Prompts

Interactive prompts to guide common tasks:
- `ollama_guide` - Interactive user guide
- `ollama_run_prompt` - Simple prompt execution
- `model_comparison` - Compare multiple models
- `fast_agent_workflow` - Multi-agent workflows
- `script_executor` - Template execution
- `batch_processing` - Multiple prompt processing
- `iterative_refinement` - Content improvement workflows

## 📁 Directory Structure

```
ollama-mcp-server/
├── src/ollama_mcp_server/
│   └── server.py                 # Main server code
├── outputs/                      # Generated output files
├── scripts/                      # Saved script templates
├── workflows/                    # Workflow definitions
├── fast-agent-scripts/          # Fast-agent Python scripts
├── prompts/                      # Usage guides
│   ├── tool_usage_guide.md
│   ├── prompt_templates_guide.md
│   └── setup_guide.md
├── example_mcp_config.json      # Claude Desktop config
└── README.md
```

## 🔧 Development

### Run Development Server
```bash
cd ollama-mcp-server
uv run python -m ollama_mcp_server.server
```

### Debug with MCP Inspector
```bash
mcp dev src/ollama_mcp_server/server.py
```

## 🛡️ Process Management

The server includes comprehensive process leak prevention:
- **Signal Handling**: Proper SIGTERM/SIGINT handling
- **Background Task Tracking**: All async tasks monitored
- **Resource Cleanup**: Automatic process termination
- **Memory Management**: Prevents accumulation of zombie processes

Monitor health with:
```bash
ps aux | grep mcp | wc -l  # Should show <10 processes
```

## 📊 Usage Examples

### Simple Prompt Execution
```
1. Use "ollama_run_prompt" prompt in Claude
2. Specify model and prompt text
3. Get immediate results
```

### Multi-Agent Workflow
```
1. Use "fast_agent_workflow" prompt
2. Choose workflow type (chain/parallel/router/evaluator)
3. Define agents and initial prompt
4. Monitor execution
```

### Script Templates
```
1. Create template with save_script
2. Use variables: {variable_name}
3. Execute with run_script
4. Pass JSON variables object
```

## 🚨 Troubleshooting

**Model not found**: Use `list_ollama_models` for exact names
**Connection issues**: Start Ollama with `ollama serve`
**High process count**: Server now prevents leaks automatically
**Job stuck**: Use `cancel_job` to stop problematic tasks

## 🤝 Contributing

1. Follow the MCP Python SDK development guidelines
2. Use proper type hints and docstrings
3. Test all new features thoroughly
4. Ensure process cleanup in all code paths

## 📄 License

This project follows the same license terms as the MCP Python SDK.

## 🙏 Acknowledgments

Built on the [Model Context Protocol](https://modelcontextprotocol.io/) and [Ollama](https://ollama.ai/) with process management patterns from MCP best practices.

---

**Ready to get started?** Check the `prompts/setup_guide.md` for detailed installation instructions!
