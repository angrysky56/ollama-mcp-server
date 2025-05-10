#!/usr/bin/env python
"""
Advanced Fast-Agent workflow using the evaluator-optimizer pattern

This workflow demonstrates how to generate high-quality content through
an iterative evaluation and optimization process, leveraging Ollama models.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent


# Create FastAgent instance - no config file needed
# The MCP server provides all necessary functionality
fast = FastAgent("Content Optimizer")

@fast.agent(
    name="content_generator",
    instruction="""You are a content generator specialized in creating high-quality,
    thoughtful content based on user requests. Be creative, accurate, and comprehensive.
    Generate content that is well-structured and engaging.""",
    model="generic.qwen3",  # Use  for creative content generation
    servers=["ollama_server"],
    use_history=True,
    human_input=True                     # agent can request human input

    # Remove request_params completely to use system defaults
)

@fast.agent(
    name="quality_evaluator",
    instruction="""You are a critical content evaluator. Your job is to review content
    and provide specific, actionable feedback on how to improve it. Rate each piece of
    content on a scale of POOR, FAIR, GOOD, or EXCELLENT.

    For anything less than EXCELLENT, provide detailed feedback on:
    1. Content accuracy and depth
    2. Structure and organization
    3. Clarity and readability
    4. Engagement and style
    5. Specific suggestions for improvement

    Always include a rating at the beginning of your response, e.g., "RATING: GOOD"
    """,
    model="generic.qwen3:32b",  # Use for evaluation
    servers=["ollama_server"],
    use_history=True,
    human_input=True                     # agent can request human input
    # Remove request_params completely to use system defaults
)

@fast.evaluator_optimizer(
    name="content_optimizer_workflow",
    generator="content_generator",
    evaluator="quality_evaluator",
    min_rating="EXCELLENT",
    max_refinements=3
)

async def main():
    """Main entry point for the content optimizer workflow"""
    async with fast.run() as agent:
        # Welcome message
        print("=== Content Optimizer Workflow ===")
        print("This workflow will generate content and iteratively improve it")
        print("until it reaches EXCELLENT quality or max refinements (3).")
        print("\nThe process uses:")
        print("- Generator: model for creative content creation")
        print("- Evaluator: model for critical assessment")
        print("\nType your content request to begin (e.g., 'Write a blog post about AI ethics')...\n")

        try:
            # Start interactive mode with the specific workflow
            await agent.content_optimizer_workflow.interactive()
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("If you're seeing model-related errors, try running with a specific model:")
            print("uv run fast-agent-scripts/content_optimizer.py --model generic.qwen3")


if __name__ == "__main__":
    asyncio.run(main())
