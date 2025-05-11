#!/usr/bin/env python
"""
Chain Workflow: code_execution_workflow
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("Code_Execution_Workflow Workflow")

@fast.agent(
    name="python_agent",
    instruction="Agent 1 in the code_execution_workflow workflow.",
    servers=["mcp-code-executor","ollama_server"]
)


@fast.chain(
    name="code_execution_workflow_workflow",
    sequence=['python_agent'],
    instruction="execute_code"
)


async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
