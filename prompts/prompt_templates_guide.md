# Built-in Prompt Templates

The Ollama MCP Server includes several built-in prompt templates to guide common tasks.

## Available Prompts

### 1. ollama_run_prompt
**Purpose**: Execute single prompts with detailed parameter guidance
**Parameters**: 
- `prompt`: The text to send to the model
- `model`: Ollama model name (default: qwen3:0.6b)
- `temperature`: Creativity level 0.0-1.0 (default: 0.7)
- `system_prompt`: Optional system instruction
- `max_tokens`: Optional token limit
- `output_format`: "text" or "json"

**Usage**: Best for simple, one-off prompt execution with step-by-step guidance.

### 2. model_comparison
**Purpose**: Compare responses from multiple models
**Parameters**:
- `prompt`: The same prompt to test across models
- `models`: Comma-separated model names
- `temperature`: Sampling temperature

**Usage**: Evaluate different models' capabilities on the same task.

### 3. fast_agent_workflow
**Purpose**: Create and execute multi-agent workflows
**Parameters**:
- `workflow_type`: "chain", "parallel", "router", or "evaluator"
- `agent_names`: Comma-separated agent names
- `initial_prompt`: Task description
- `model`: Optional default model

**Usage**: Complex multi-step tasks requiring agent coordination.

### 4. script_executor
**Purpose**: Execute saved script templates with variables
**Parameters**:
- `script_name`: Name of saved script
- `model`: Ollama model to use
- `variables`: JSON object with variable substitutions

**Usage**: Reusable prompt templates with dynamic content.

### 5. model_analysis
**Purpose**: Analyze model capabilities and performance
**Parameters**:
- `model`: Model to analyze
- `analysis_type`: Type of analysis (default: "capabilities")
- `test_prompts`: Comma-separated test prompts

**Usage**: Systematic evaluation of model performance.

### 6. iterative_refinement
**Purpose**: Improve output through generator-evaluator pattern
**Parameters**:
- `initial_prompt`: Starting prompt
- `generator_model`: Model for content generation
- `evaluator_model`: Model for evaluation
- `min_rating`: Minimum quality threshold
- `max_iterations`: Maximum refinement cycles

**Usage**: High-quality content requiring iterative improvement.

### 7. batch_processing
**Purpose**: Process multiple prompts efficiently
**Parameters**:
- `prompts`: JSON array of prompts
- `model`: Model to use for all prompts
- `parallel`: Process simultaneously or sequentially
- `output_format`: Output format for all prompts

**Usage**: Large-scale prompt processing tasks.

### 8. conversation_flow
**Purpose**: Manage multi-turn conversations with context
**Parameters**:
- `initial_prompt`: Starting conversation
- `model`: Model for conversation
- `max_turns`: Maximum conversation length
- `context_window`: Context size limit

**Usage**: Interactive conversations with memory management.

### 9. ollama_guide
**Purpose**: Interactive guide for new users
**Parameters**: None

**Usage**: Help users understand available tools and workflows.

## How to Use Prompts

1. **Access via MCP Client**: Prompts appear in your MCP client's prompt menu
2. **Fill Parameters**: Provide required and optional parameters
3. **Execute**: The prompt guides you through using the appropriate tools
4. **Follow Steps**: Each prompt provides step-by-step instructions

## Custom Prompts

You can create custom prompts by:
1. Saving script templates with `save_script`
2. Using variable substitution: `{variable_name}`
3. Including system prompts: `SYSTEM: your system instruction`
4. Executing with `run_script`

## Tips

- Start with `ollama_guide` if you're new
- Use `ollama_run_prompt` for simple tasks
- Use `fast_agent_workflow` for complex multi-step tasks
- Use `script_executor` for reusable templates
- Check model availability with prompts that include validation steps
