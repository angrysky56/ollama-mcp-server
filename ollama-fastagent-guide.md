# Ollama MCP + Fast-Agent Integration Guide

This guide explains how to integrate Ollama with fast-agent to create powerful, composable AI workflows and agent systems. The existing implementation in this repository provides a foundation for advanced agent interactions using Ollama models.

## Repository Structure

The repository currently follows this structure:

```
ollama-mcp-server/
├── fast-agent-scripts/   # Fast-agent script implementations
├── outputs/              # Output files from execution
├── scripts/              # Script templates for Ollama
├── src/                  # Source code
│   ├── ollama_mcp_server/  # MCP server implementation
└── workflows/        # Workflow definitions
...
```

This structure differs from what's described in the README but is organized in a way that makes sense for your use case, keeping related files together.

## Components Overview

### 1. Ollama MCP Server

The Ollama MCP Server is implemented in `src/ollama_mcp_server/server.py`. It provides an MCP server interface for running Ollama models, with the following capabilities:

- **Model Management**: List available Ollama models
- **Prompt Execution**: Run prompts with different Ollama models
- **Job Management**: Track and manage running jobs
- **Script Handling**: Save and run script templates
- **Fast-Agent Integration**: Create and run fast-agent scripts

### 2. Fast-Agent Integration

Fast-agent is integrated through:
# 1 doesn't make sense, tools should be integrated into the server.py and scripts should be in the fast-agent-scripts directory. config is deprecated.
1. The `fastagent.config.yaml` file that defines the ollama_server as an MCP server
2. The `fast-agent-scripts` directory containing agent implementations
3. MCP tools in the server for managing fast-agent scripts

## Using Fast-Agent with Ollama

### Basic Agent

The simplest integration is a basic agent that uses Ollama models:

```python
#!/usr/bin/env python
"""
Basic Fast-Agent using Ollama
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("My Agent")

@fast.agent(
    name="my_agent",
    instruction="You are a helpful AI assistant.",
    model="phi4-reasoning:14b-plus-q4_K_M",  # Specify an Ollama model
    servers=["ollama_server"]  # Reference the MCP server
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

This script creates a single agent that uses the specified Ollama model.

### Chain Workflow

For more complex scenarios, you can create a chain of agents:

```python
@fast.agent(
    name="researcher",
    instruction="Research topics thoroughly.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.agent(
    name="summarizer",
    instruction="Summarize information concisely.",
    model="qwen3:0.6b",  # Using a different model for summarization
    servers=["ollama_server"]
)

@fast.chain(
    name="research_workflow",
    sequence=["researcher", "summarizer"],
    instruction="Research and summarize information."
)

async def main():
    async with fast.run() as agent:
        await agent.interactive()
```

This creates a workflow where the output from the researcher agent is passed to the summarizer agent.

### Parallel Workflow with Model Ensemble

You can run multiple models in parallel and aggregate their outputs:

```python
@fast.agent(
    name="model1_agent",
    instruction="First model perspective.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.agent(
    name="model2_agent",
    instruction="Second model perspective.",
    model="gemma3:latest",
    servers=["ollama_server"]
)

@fast.agent(
    name="aggregator",
    instruction="Combine and analyze multiple perspectives.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.parallel(
    name="ensemble_workflow",
    fan_out=["model1_agent", "model2_agent"],
    fan_in="aggregator"
)
```

This creates a parallel workflow where multiple models process the same input, and their outputs are aggregated.

### Evaluator-Optimizer Pattern

For iterative content improvement:

```python
@fast.agent(
    name="generator",
    instruction="Generate content based on requests.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.agent(
    name="evaluator",
    instruction="Evaluate content and provide feedback. Rate as POOR, FAIR, GOOD, or EXCELLENT.",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.evaluator_optimizer(
    name="optimizer_workflow",
    generator="generator",
    evaluator="evaluator",
    min_rating="EXCELLENT",
    max_refinements=3
)
```

This creates a workflow that iteratively improves content until it reaches the specified quality threshold or maximum number of refinements.

## Running Fast-Agent Scripts

To run a fast-agent script:

```bash
cd /path/to/ollama-mcp-server
uv run src/fast-agent-scripts/your_script.py
```

For specific agent targets:

```bash
uv run src/fast-agent-scripts/your_script.py --agent my_agent_name
```

With a specific message:

```bash
uv run src/fast-agent-scripts/your_script.py --agent my_agent_name --message "Your prompt"
```

## Creating New Fast-Agent Scripts

You can create new scripts directly through the MCP tools:

1. Connect to the MCP server
2. Use the `create_fastagent_script` tool to create a new script
3. Use the `update_fastagent_script` tool to modify existing scripts
4. Use the `run_fastagent_script` tool to execute scripts

## Configuration

The `fastagent.config.yaml` file defines the available MCP servers:

```yaml
# MCP Servers configuration
mcp:
  ollama_server:
    # Direct reference to local Ollama MCP server
    command: "uv"
    args: ["run", "-m", "src.ollama_mcp_server.server"]
```

This configuration makes the Ollama MCP server available to fast-agent scripts.

## Advanced Usage

### Using Different Models

You can specify different Ollama models for each agent:

```python
@fast.agent(
    name="agent1",
    instruction="First instruction",
    model="phi4-reasoning:14b-plus-q4_K_M",
    servers=["ollama_server"]
)

@fast.agent(
    name="agent2",
    instruction="Second instruction",
    model="qwen3:0.6b",
    servers=["ollama_server"]
)
```

### Router Workflow

For dynamic agent selection based on the input:

```python
@fast.router(
    name="router_workflow",
    agents=["agent1", "agent2", "agent3"],
    instruction="Route the request to the most appropriate agent"
)
```

### Orchestrator for Complex Tasks

For complex workflows with multiple steps:

```python
@fast.orchestrator(
    name="orchestrator_workflow",
    agents=["agent1", "agent2", "agent3"],
    instruction="Plan and execute a complex task"
)
```

## Sample Workflows

The repository includes several example workflows:

1. **Basic Agent**: Simple interaction with a single model
2. **Chain Workflow**: Sequential processing through multiple agents
3. **Model Ensemble**: Parallel processing with different models
4. **Content Optimizer**: Iterative improvement using evaluation feedback

Refer to the `fast-agent-scripts` directory for implementation examples.

## Troubleshooting

If you encounter issues:

1. Ensure Ollama is running (`ollama serve`)
2. Check model availability with `ollama list`
3. Verify the `fastagent.config.yaml` configuration
4. Check script syntax and model names
5. Restart Claude Desktop after making changes to the Ollama MCP server

## Next Steps

1. Experiment with different agent combinations
2. Test various Ollama models for different tasks
3. Create specialized agents for specific domains
4. Develop more complex workflows for real-world applications

The integration of Ollama with fast-agent provides a powerful platform for building sophisticated AI systems with specialized components.
