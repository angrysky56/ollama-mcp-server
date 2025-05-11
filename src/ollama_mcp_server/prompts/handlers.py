"""Prompt handlers for Ollama MCP server."""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable
from mcp.types import PromptMessage, TextContent, PromptArgument
from ..server import OllamaMCPServer

logger = logging.getLogger(__name__)


def get_prompt_handlers(server: OllamaMCPServer) -> Dict[str, Callable[[Dict[str, Any]], Awaitable[List[PromptMessage]]]]:
    """Get handlers for each prompt type.
    
    Args:
        server: The OllamaMCPServer instance to bind handlers to
        
    Returns:
        Dict mapping prompt names to their handler functions
    """
    
    async def handle_run_prompt(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the run-prompt prompt."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Run this prompt with the specified Ollama model:

Prompt: {arguments.get('prompt', '')}
Model: {arguments.get('model', 'qwen3:0.6b')}
Temperature: {arguments.get('temperature', 0.7)}
System Prompt: {arguments.get('system_prompt', '')}
Max Tokens: {arguments.get('max_tokens', 'default')}
Output Format: {arguments.get('output_format', 'text')}

Please process this request using the Ollama model."""
                ),
            )
        ]
    
    async def handle_model_comparison(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the model-comparison prompt."""
        models = arguments.get('models', '').split(',')
        models = [m.strip() for m in models if m.strip()]
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Compare responses from multiple Ollama models:

Prompt: {arguments.get('prompt', '')}
Models: {', '.join(models)}
Temperature: {arguments.get('temperature', 0.7)}

Please run this prompt through each model and compare their outputs."""
                ),
            )
        ]
    
    async def handle_fast_agent_workflow(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the fast-agent-workflow prompt."""
        agents = arguments.get('agent_names', '').split(',')
        agents = [a.strip() for a in agents if a.strip()]
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Set up a fast-agent workflow:

Workflow Type: {arguments.get('workflow_type', 'chain')}
Agents: {', '.join(agents)}
Initial Prompt: {arguments.get('initial_prompt', '')}
Default Model: {arguments.get('model', 'phi4-reasoning:14b-plus-q4_K_M')}

Create and run this workflow configuration."""
                ),
            )
        ]
    
    async def handle_script_executor(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the script-executor prompt."""
        variables = {}
        if arguments.get('variables'):
            try:
                variables = json.loads(arguments['variables'])
            except json.JSONDecodeError:
                pass
                
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Execute a saved script template:

Script Name: {arguments.get('script_name', '')}
Model: {arguments.get('model', 'qwen3:0.6b')}
Variables: {json.dumps(variables, indent=2)}

Load and execute this script with the specified variables."""
                ),
            )
        ]
    
    async def handle_model_analysis(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the model-analysis prompt."""
        test_prompts = []
        if arguments.get('test_prompts'):
            test_prompts = [p.strip() for p in arguments['test_prompts'].split(',') if p.strip()]
            
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Analyze an Ollama model's capabilities:

Model: {arguments.get('model', '')}
Analysis Type: {arguments.get('analysis_type', 'capabilities')}
Test Prompts: {json.dumps(test_prompts, indent=2) if test_prompts else 'None'}

Please conduct the specified analysis on this model."""
                ),
            )
        ]
    
    async def handle_iterative_refinement(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the iterative-refinement prompt."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Apply iterative refinement pattern:

Initial Prompt: {arguments.get('initial_prompt', '')}
Generator Model: {arguments.get('generator_model', 'phi4-reasoning:14b-plus-q4_K_M')}
Evaluator Model: {arguments.get('evaluator_model', 'phi4-reasoning:14b-plus-q4_K_M')}
Minimum Rating: {arguments.get('min_rating', 'GOOD')}
Max Iterations: {arguments.get('max_iterations', '3')}

Run this evaluator-optimizer workflow to refine the output."""
                ),
            )
        ]
    
    async def handle_batch_processing(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the batch-processing prompt."""
        prompts = []
        if arguments.get('prompts'):
            try:
                prompts = json.loads(arguments['prompts'])
            except json.JSONDecodeError:
                pass
                
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Process multiple prompts in batch:

Prompts: {json.dumps(prompts, indent=2) if prompts else 'Invalid JSON'}
Model: {arguments.get('model', 'qwen3:0.6b')}
Parallel Processing: {arguments.get('parallel', 'false')}
Output Format: {arguments.get('output_format', 'text')}

Process these prompts using the specified configuration."""
                ),
            )
        ]
    
    async def handle_conversation_flow(arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Handle the conversation-flow prompt."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Set up a conversation flow:

Initial Prompt: {arguments.get('initial_prompt', '')}
Model: {arguments.get('model', 'phi4-reasoning:14b-plus-q4_K_M')}
Max Turns: {arguments.get('max_turns', '5')}
Context Window: {arguments.get('context_window', '4096')}

Initialize and manage this conversation flow with context retention."""
                ),
            )
        ]
    
    # Return mapping of prompt names to handlers
    return {
        "run-prompt": handle_run_prompt,
        "model-comparison": handle_model_comparison,
        "fast-agent-workflow": handle_fast_agent_workflow,
        "script-executor": handle_script_executor,
        "model-analysis": handle_model_analysis,
        "iterative-refinement": handle_iterative_refinement,
        "batch-processing": handle_batch_processing,
        "conversation-flow": handle_conversation_flow,
    }
