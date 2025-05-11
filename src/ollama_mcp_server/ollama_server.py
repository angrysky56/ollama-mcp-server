#!/usr/bin/env python
"""
Ollama MCP Server with prompts support.
"""

import asyncio
from typing import Dict, Any, List
from pathlib import Path
import json
import sys

# Add parent directory to path to enable imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server import (
    Server,
    StdioServerFactory,
    NotificationOptions
)
from mcp.types import (
    Prompt,
    PromptMessage,
    GetPromptResult,
    ListPromptsResult,
    GetPromptRequest,
    ListPromptsRequest,
    INTERNAL_ERROR,
    TextContent
)

# Import existing server functionality
from .server import (
    BASE_DIR,
    OUTPUTS_DIR,
    SCRIPTS_DIR,
    WORKFLOWS_DIR,
    FASTAGENT_DIR,
    mcp,
    list_ollama_models,
    run_ollama_prompt,
    get_job_status,
    cancel_job,
    list_jobs,
    save_script,
    list_scripts,
    get_script,
    run_script,
    run_bash_command,
    run_workflow,
    list_fastagent_scripts,
    create_fastagent_script,
    get_fastagent_script,
    update_fastagent_script,
    delete_fastagent_script,
    run_fastagent_script,
    create_fastagent_workflow
)

# Import prompts system
from .prompts import get_prompt_manager, get_prompt_handlers
from .prompts.prompts import PROMPTS


class OllamaMCPServer:
    """Enhanced MCP server with prompts support."""
    
    def __init__(self):
        """Initialize the server with FastMCP and prompts support."""
        self.server = mcp
        
        # Initialize prompt handlers
        self.prompt_handlers = get_prompt_handlers(self)
        
        # Add prompt handlers to the server
        self.register_prompts()
    
    def register_prompts(self):
        """Register prompts with the MCP server."""
        
        async def list_prompts_handler(request: ListPromptsRequest) -> ListPromptsResult:
            """Handle list_prompts request."""
            prompt_manager = get_prompt_manager()
            prompts_list = list(prompt_manager.values())
            
            return ListPromptsResult(prompts=prompts_list)
        
        async def get_prompt_handler(request: GetPromptRequest) -> GetPromptResult:
            """Handle get_prompt request."""
            try:
                prompt_name = request.params.name
                prompt_manager = get_prompt_manager()
                prompt = prompt_manager.get(prompt_name)
                
                if not prompt:
                    raise ValueError(f"Prompt '{prompt_name}' not found")
                
                # Get arguments from request
                arguments = request.params.arguments
                
                # Get the handler for this prompt
                handler = self.prompt_handlers.get(prompt_name)
                if not handler:
                    # Return a generic prompt if no specific handler
                    return GetPromptResult(
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=f"Prompt '{prompt_name}' is registered but has no handler."
                                )
                            )
                        ]
                    )
                
                # Use the handler to generate messages
                messages = await handler(arguments)
                return GetPromptResult(messages=messages)
                
            except Exception as e:
                return GetPromptResult(
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"Error executing prompt: {str(e)}"
                            )
                        )
                    ]
                )
        
        # Register the handlers with FastMCP
        @self.server.server.response_handler(ListPromptsRequest)
        async def list_prompts_wrapper():
            """Wrapper for list_prompts handler."""
            return await list_prompts_handler(ListPromptsRequest())
            
        @self.server.server.response_handler(GetPromptRequest)
        async def get_prompt_wrapper(request: GetPromptRequest):
            """Wrapper for get_prompt handler."""
            return await get_prompt_handler(request)
        
    async def run(self):
        """Run the MCP server."""
        await self.server.run()


async def main():
    """Run the server."""
    server = OllamaMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
