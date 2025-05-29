# Ollama MCP Server Tool Usage Guide

## Quick Start

This Ollama MCP Server provides comprehensive tools for running Ollama models with advanced features like script management, workflow creation, and fast-agent integration.

## Essential Tools

### Basic Operations
- **list_ollama_models**: Show all available Ollama models with sizes
- **run_ollama_prompt**: Execute prompts with any Ollama model
- **get_job_status**: Check completion status of running jobs
- **list_jobs**: View all running and completed jobs
- **cancel_job**: Stop a running job

### Script Management
- **save_script**: Create reusable prompt templates with variables
- **list_scripts**: View all saved script templates
- **get_script**: Read content of a specific script
- **run_script**: Execute scripts with variable substitution

### Fast-Agent Workflows
- **create_fastagent_script**: Create single-agent scripts
- **create_fastagent_workflow**: Build multi-agent workflows (chain, parallel, router, evaluator)
- **run_fastagent_script**: Execute fast-agent scripts/workflows
- **list_fastagent_scripts**: View available fast-agent scripts

### System Commands
- **run_bash_command**: Execute system commands safely
- **run_workflow**: Execute complex multi-step workflows

## Common Usage Patterns

### 1. Simple Prompt Execution
```
1. list_ollama_models (verify model availability)
2. run_ollama_prompt (execute with wait_for_result=true)
```

### 2. Async Job Management
```
1. run_ollama_prompt (with wait_for_result=false)
2. get_job_status (poll until complete)
3. View results in output file
```

### 3. Script-Based Workflows
```
1. save_script (create reusable template)
2. run_script (execute with variables)
3. get_job_status (monitor completion)
```

### 4. Multi-Agent Workflows
```
1. create_fastagent_workflow (define agent chain/parallel/router)
2. run_fastagent_script (execute workflow)
3. get_job_status (monitor progress)
```

## Best Practices

1. **Always validate models**: Use `list_ollama_models` to get exact model names
2. **Use descriptive names**: For scripts and workflows to aid organization
3. **Monitor long-running tasks**: Use `get_job_status` for async operations
4. **Start simple**: Begin with `wait_for_result=true` for immediate feedback
5. **Check outputs**: Review generated files for complete results

## Error Handling

- **"Model not found"**: Use `list_ollama_models` for correct names
- **"Script not found"**: Check exact name with `list_scripts`
- **"Invalid workflow type"**: Use: chain, parallel, router, evaluator
- **"Timeout errors"**: Increase timeout or use async execution

## Output Management

All operations create output files in the `outputs/` directory:
- Standard jobs: `{job_id}.txt`
- Bash commands: `{job_id}_bash.txt`
- Fast-agent scripts: `{job_id}_fastagent.txt`
- Workflows: `{run_id}_workflow.txt`

Files contain metadata, commands, and results for full traceability.
