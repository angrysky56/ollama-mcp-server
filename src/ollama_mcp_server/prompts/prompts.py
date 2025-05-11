"""Prompt definitions for Ollama MCP server."""

from mcp.types import (
    Prompt,
    PromptArgument,
)

# Define all prompts for Ollama integration
PROMPTS = {
    "run-prompt": Prompt(
        name="run-prompt",
        description="Run a prompt with specified Ollama model",
        arguments=[
            PromptArgument(
                name="prompt", description="The prompt to run", required=True
            ),
            PromptArgument(
                name="model", description="Ollama model to use", required=True
            ),
            PromptArgument(
                name="temperature",
                description="Sampling temperature (0.0 to 1.0)",
                required=False,
            ),
            PromptArgument(
                name="system_prompt",
                description="Optional system prompt",
                required=False,
            ),
            PromptArgument(
                name="max_tokens",
                description="Maximum tokens to generate",
                required=False,
            ),
            PromptArgument(
                name="output_format",
                description="Output format: text or json",
                required=False,
            ),
        ],
    ),
    "model-comparison": Prompt(
        name="model-comparison",
        description="Compare responses from multiple models",
        arguments=[
            PromptArgument(
                name="prompt", description="The prompt to run", required=True
            ),
            PromptArgument(
                name="models",
                description="Comma-separated list of models to compare",
                required=True,
            ),
            PromptArgument(
                name="temperature",
                description="Sampling temperature (0.0 to 1.0)",
                required=False,
            ),
        ],
    ),
    "fast-agent-workflow": Prompt(
        name="fast-agent-workflow",
        description="Run a fast-agent workflow",
        arguments=[
            PromptArgument(
                name="workflow_type",
                description="Type of workflow (chain/parallel/router/evaluator)",
                required=True,
            ),
            PromptArgument(
                name="agent_names",
                description="Comma-separated list of agent names",
                required=True,
            ),
            PromptArgument(
                name="initial_prompt",
                description="Initial prompt for the workflow",
                required=True,
            ),
            PromptArgument(
                name="model",
                description="Default Ollama model for agents",
                required=False,
            ),
        ],
    ),
    "script-executor": Prompt(
        name="script-executor",
        description="Execute saved script template with variables",
        arguments=[
            PromptArgument(
                name="script_name", description="Name of the script", required=True
            ),
            PromptArgument(
                name="model", description="Ollama model to use", required=True
            ),
            PromptArgument(
                name="variables",
                description="JSON string of variables for substitution",
                required=False,
            ),
        ],
    ),
    "model-analysis": Prompt(
        name="model-analysis",
        description="Analyze model capabilities and performance",
        arguments=[
            PromptArgument(
                name="model", description="Ollama model to analyze", required=True
            ),
            PromptArgument(
                name="analysis_type",
                description="Type of analysis (capabilities/performance/comparison)",
                required=False,
            ),
            PromptArgument(
                name="test_prompts",
                description="Comma-separated list of test prompts",
                required=False,
            ),
        ],
    ),
    "iterative-refinement": Prompt(
        name="iterative-refinement",
        description="Iteratively refine output using evaluator pattern",
        arguments=[
            PromptArgument(
                name="initial_prompt",
                description="The initial prompt to generate content",
                required=True,
            ),
            PromptArgument(
                name="generator_model",
                description="Model for generating content",
                required=True,
            ),
            PromptArgument(
                name="evaluator_model",
                description="Model for evaluating content",
                required=True,
            ),
            PromptArgument(
                name="min_rating",
                description="Minimum quality rating (POOR/FAIR/GOOD/EXCELLENT)",
                required=False,
            ),
            PromptArgument(
                name="max_iterations",
                description="Maximum refinement iterations",
                required=False,
            ),
        ],
    ),
    "batch-processing": Prompt(
        name="batch-processing",
        description="Process multiple prompts in batch",
        arguments=[
            PromptArgument(
                name="prompts",
                description="JSON array of prompts to process",
                required=True,
            ),
            PromptArgument(
                name="model", description="Ollama model to use", required=True
            ),
            PromptArgument(
                name="parallel",
                description="Process in parallel (true/false)",
                required=False,
            ),
            PromptArgument(
                name="output_format",
                description="Output format: text or json",
                required=False,
            ),
        ],
    ),
    "conversation-flow": Prompt(
        name="conversation-flow",
        description="Manage conversation flow with context retention",
        arguments=[
            PromptArgument(
                name="initial_prompt",
                description="Starting prompt for conversation",
                required=True,
            ),
            PromptArgument(
                name="model", description="Ollama model to use", required=True
            ),
            PromptArgument(
                name="max_turns",
                description="Maximum conversation turns",
                required=False,
            ),
            PromptArgument(
                name="context_window",
                description="Context window size",
                required=False,
            ),
        ],
    ),
}
