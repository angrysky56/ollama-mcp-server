#!/usr/bin/env python
"""
Advanced Fast-Agent example using the CognitiveComputations/dolphin-mistral-nemo:12b model.

This script creates a more sophisticated interactive agent designed for complex
problem-solving, research, and task execution using a variety of MCP tools.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance.
# The name here is for the FastAgent application instance, not the agent itself.
fast_app = FastAgent("polymath_suite")

# Define the Advanced Agent
@fast_app.agent(
    name="PolymathAssistant",
    instruction=(
        "You are PolymathAssistant, an advanced AI with a calm, analytical, and "
        "resourceful persona. Your primary goal is to assist users by deeply "
        "understanding their requests, breaking down complex problems into manageable steps, "
        "and strategically utilizing your available tools to find information, "
        "execute tasks, or generate creative content.\n\n"
        "Before acting, briefly outline your plan or the tools you intend to use. "
        "If a query is ambiguous, ask clarifying questions. "
        "If one tool doesn't yield the desired result, consider if an alternative "
        "tool or a modified approach is necessary. "
        "Strive for comprehensive and accurate responses. "
        "You have access to tools for web searching, academic research, coding, "
        "file system operations, and more; use them wisely."
    ),
    use_history=True,  # Maintain conversation context
    model="generic.qwen3-4b-code-32k", # Specified model
    # Ensure these servers are correctly defined in your fastagent.config.yaml
    servers=[
        "ollama_server",        # Essential for running the specified model if it's local
        "ai-writers-workshop",  # For creative writing tasks
        "mcp-logic",            # For logical reasoning or knowledge base queries
        "arxiv-mcp-server",     # For accessing and searching arXiv papers
        "desktop-commander",    # For file system access and local command execution
        "brave-search",         # For general web searching
        "mcp-code-executor",    # For executing code snippets
        "sqlite",               # For interacting with SQLite databases
        "puppeteer"             # For web browser automation and scraping
    ]
)
async def polymath_workflow(agent_session):
    """
    This function can be developed to define a more structured workflow
    for the PolymathAssistant if needed, beyond the default interactive mode.
    For now, we'll use the interactive mode.
    """
    print("=== PolymathAssistant Online ===")
    print("Model: CognitiveComputations/dolphin-mistral-nemo:12b")
    print("Specialized in: Research, Code, System Interaction, and Creative Tasks.")
    print("\nAvailable Tool Categories (via MCP Servers):")
    print("- Local Model Execution (ollama_server)")
    print("- Creative Writing (ai-writers-workshop)")
    print("- Logical Reasoning/KB (mcp-logic)")
    print("- Academic Research (arxiv-mcp-server)")
    print("- Desktop Operations (desktop-commander)")
    print("- Web Search (brave-search)")
    print("- Code Execution (mcp-code-executor)")
    print("- Database Interaction (sqlite)")
    print("- Web Automation/Scraping (puppeteer)")
    print("\nHow can I assist you today?\n")

    try:
        # Using the interactive mode for direct user interaction.
        # The agent_session passed here is the one created by fast.run()
        await agent_session.interactive(agent="PolymathAssistant")
    except Exception as e:
        print(f"\nAn error occurred during the PolymathAssistant session: {str(e)}")
        print("Troubleshooting tips:")
        print("1. Ensure the Ollama server is running and the model selected in polymath_workflow.py is available ('ollama list').")
        print("2. Verify all MCP servers listed in the agent's configuration are running and accessible.")
        print("3. Check your `fastagent.config.yaml` for any misconfigurations.")

async def main():
    # fast.run() provides the agent session
    async with fast_app.run() as agent_session:
        # Here, agent_session is the specific session for this run.
        # We pass it to the workflow function.
        await polymath_workflow(agent_session)

if __name__ == "__main__":
    asyncio.run(main())