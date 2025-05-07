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
    model="passthrough"  # Using passthrough model to avoid compatibility issues
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
    model="passthrough"  # Using passthrough model to avoid compatibility issues
)

@fast.evaluator_optimizer(
    name="content_optimizer_workflow",
    generator="content_generator",
    evaluator="quality_evaluator",
    min_rating="EXCELLENT",
    max_refinements=3,
)

async def main():
    """Main entry point for the content optimizer workflow"""
    async with fast.run() as agent:
        # Welcome message
        print("=== Content Optimizer Workflow ===")
        print("This workflow will generate content and iteratively improve it")
        print("until it reaches EXCELLENT quality or max refinements.")
        print("Type your content request to begin...\n")

        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
