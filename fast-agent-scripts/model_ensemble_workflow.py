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
    name="phi4_agent",
    instruction="You are the phi4-reasoning model agent. You excel at logical reasoning and structured thinking. Provide detailed, analytical responses with careful step-by-step reasoning.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.agent(
    name="gemma_agent",
    instruction="You are the gemma3 model agent. You excel at creative thinking and nuanced responses. Focus on providing insightful perspectives that others might miss.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.agent(
    name="qwen_agent",
    instruction="You are the qwen3 model agent. You excel at concise, practical responses with a focus on accuracy and relevance. Be direct and to the point.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.agent(
    name="aggregator",
    instruction="You are the ensemble aggregator. Your job is to analyze multiple model responses, identify where they agree and disagree, and synthesize a comprehensive response that leverages the strengths of each model.",
    model="passthrough"  # Using passthrough to avoid model compatibility issues
)

@fast.parallel(
    name="model_ensemble_workflow",
    fan_out=["phi4_agent", "gemma_agent", "qwen_agent"],
    fan_in="aggregator",
    instruction="Run multiple Ollama models in parallel to generate diverse responses, then aggregate the results to provide a comprehensive analysis."
)

async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
