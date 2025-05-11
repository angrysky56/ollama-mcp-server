"""Prompts module for Ollama MCP server."""

from .prompt_manager import get_prompt_manager, register_prompt
from .prompts import PROMPTS
from .handlers import get_prompt_handlers

__all__ = [
    "get_prompt_manager",
    "register_prompt",
    "PROMPTS",
    "get_prompt_handlers",
]
