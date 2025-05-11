"""Ollama prompt management for the MCP server."""

from typing import Dict, Optional
from mcp.types import Prompt
from .prompts import PROMPTS

# Global prompt manager instance
_prompt_manager: Optional[Dict[str, Prompt]] = None


def get_prompt_manager() -> Dict[str, Prompt]:
    """Get or create the global prompt manager dictionary.

    Returns:
        Dict[str, Prompt]: Dictionary of available prompts
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PROMPTS.copy()

    return _prompt_manager


def register_prompt(prompt: Prompt) -> None:
    """Register a new prompt in the prompt manager.

    Args:
        prompt (Prompt): The prompt to register
    """
    manager = get_prompt_manager()
    manager[prompt.name] = prompt


def get_prompt(name: str) -> Optional[Prompt]:
    """Get a prompt by name.

    Args:
        name (str): The name of the prompt to retrieve

    Returns:
        Optional[Prompt]: The prompt if found, None otherwise
    """
    manager = get_prompt_manager()
    return manager.get(name)


def list_prompts() -> list[str]:
    """List all registered prompt names.

    Returns:
        list[str]: List of prompt names
    """
    manager = get_prompt_manager()
    return list(manager.keys())
