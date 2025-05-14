#!/usr/bin/env python
"""
Parallel Workflow: model_ensemble

This workflow demonstrates running multiple Ollama models in parallel to generate
diverse responses to the same prompt, then combines their outputs for a more
comprehensive analysis.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent


# Create FastAgent instance
fast = FastAgent("Model Ensemble Workflow")

@fast.agent(
    name="research_agent",
    instruction="""You are a research agent that excels at logical reasoning and structured thinking.
    Provide detailed, analytical responses with careful step-by-step reasoning.

    When a question involves research topics or papers use search for relevant information.
    """,
    model="generic.qwen3:14b",  # Use model that supports tool usage
    servers=["ollama_server", "arxiv-mcp-server", "brave-search", "desktop-commander"],
    use_history=True,
    # Remove request_params completely to use system defaults
)

@fast.agent(
    name="creative_agent",
    instruction="""You are a creative agent that excels at creative thinking and nuanced responses.
    Focus on providing insightful perspectives that others might miss.
    """,
    model="generic.qwen3:30b-a3b",  # Good for creative responses
    servers=["ollama_server", "arxiv-mcp-server", "desktop-commander", "brave-search"],
    use_history=True,
    # Remove request_params completely to use system defaults
)

@fast.agent(
    name="tool_agent",
    instruction="""You are a specialized tool-using agent. You excel at automation and practical responses.

    You have access to tools - use them proactively when appropriate:

    Analyze requests carefully to determine which tools would be most helpful.
    """,
    model="generic.qwen3:14b",  # Qwen has better tool capabilities
    servers=["ollama_server", "arxiv-mcp-server", "desktop-commander", "brave-search"],
    use_history=True,
    # Remove request_params completely to use system defaults
)

@fast.agent(
    name="aggregator",
    instruction="""You are the ensemble aggregator. Your job is to analyze multiple agent responses, identify where they agree and disagree,
    and synthesize a comprehensive response that leverages the strengths of each agent.

    For each response you'll see:
    1. A logical analysis from the research agent
    2. A creative perspective from the creative agent
    3. A practical approach with tool use from the tool agent

    IMPORTANT:

    Analyze the responses carefully, noting:
    - Where models agree (high confidence information)
    - Where models disagree (areas of uncertainty)
    - Unique insights from each model
    - Tool-generated data from the tool agent

    Then create a unified response that:
    1. Integrates the logical structure from the research agent
    2. Incorporates creative insights from the creative agent
    3. Leverages practical tool-based information from the tool agent
    4. Highlights areas of model agreement and disagreement

    """,

    model="generic.qwen3:30b-a3b",
    servers=["ollama_server", "brave-search"],  # Limited server access for aggregator
    use_history=True,
    # Remove request_params completely to use system defaults
)

@fast.parallel(
    name="model_ensemble_workflow",
    fan_out=["research_agent", "creative_agent", "tool_agent"],
    fan_in="aggregator",
)

async def main():
    async with fast.run() as agent:
        # Welcome and instructions
        print("=== Multi-Model Ensemble Workflow ===")
        print("This workflow leverages multiple models in parallel:")
        print("1. Research: Logical analysis and structured reasoning")
        print("2. Creative: Creative perspectives and nuanced insights")
        print("3. Tool Use: Practical tool use and information retrieval")
        print("\nThe outputs are then combined by an aggregator model.")
        print("\nSuggested queries to try:")
        print("- Research questions (leverages arxiv-mcp-server)")
        print("- Web content analysis (leverages brave-search tool)")
        print("- System information requests (leverages desktop-commander)")
        print("- Complex problems requiring multiple perspectives")
        print("\nType your query to begin...\n")

        try:
            # For parallel workflows, we use the agent's interactive mode and specify which workflow to use
            await agent.interactive(agent="model_ensemble_workflow")
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("If you're seeing model-related errors, consider:")
            print("1. Checking if the specified models are available with 'ollama list'")
            print("2. Running with a different model:")
            print("   uv run fast-agent-scripts/model_ensemble_workflow.py --model generic.qwen3:30b-a3b")

if __name__ == "__main__":
    asyncio.run(main())
