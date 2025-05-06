"""
Improved run_workflow function for the Ollama MCP Server.
This addresses the tool lookup issues in the workflow tool.
"""

async def run_workflow(
    steps,
    wait_for_completion=False
):
    """
    Run a workflow of multiple steps sequentially.

    Args:
        steps: List of step dictionaries, each containing:
               - tool: Name of the tool to call (e.g., "run_ollama_prompt")
               - params: Parameters to pass to the tool
        wait_for_completion: Whether to wait for all steps to complete

    Returns:
        Dict with workflow execution status
    """
    import asyncio
    import json
    import os
    import uuid
    import time
    from pathlib import Path

    # Get our module's global namespace to access tool functions- no modules imported so commented out
    # import sys
    # module = sys.modules[__name__]

    # Use the environment variable for the base directory
    if os.environ.get("OLLAMA_MCP_ROOT"):
        BASE_DIR = Path(os.environ["OLLAMA_MCP_ROOT"])
    else:
        BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent

    # Output directories
    OUTPUTS_DIR = BASE_DIR / "outputs"
    SCRIPTS_DIR = BASE_DIR / "scripts"
    WORKFLOWS_DIR = BASE_DIR / "workflows"

    # Generate a unique workflow run ID
    run_id = str(uuid.uuid4())
    output_file = OUTPUTS_DIR / f"{run_id}_workflow.txt"

    # Write metadata to the output file
    with open(output_file, "w") as f:
        metadata = {
            "run_id": run_id,
            "started_at": time.time(),
            "steps_count": len(steps),
            "current_dir": os.getcwd(),
            "base_dir": str(BASE_DIR),
            "outputs_dir": str(OUTPUTS_DIR)
        }
        f.write(f"WORKFLOW RUN: {json.dumps(metadata)}\n\n")
        f.write(f"OUTPUT DIR: {OUTPUTS_DIR}\n")
        f.write(f"SCRIPTS DIR: {SCRIPTS_DIR}\n")
        f.write(f"WORKFLOWS DIR: {WORKFLOWS_DIR}\n\n")

    # Function to execute the workflow steps
    async def execute_workflow():
        # Import necessary functions
        from ollama_mcp_server.server import (
            list_ollama_models, run_ollama_prompt, get_job_status,
            cancel_job, list_jobs, save_script, list_scripts,
            get_script, run_script, run_bash_command
        )

        results = []

        for i, step in enumerate(steps):
            step_num = i + 1
            tool_name = step.get("tool")
            params = step.get("params", {})
            name = step.get("name", f"Step {step_num}")

            # Skip step if it has no tool name
            if not tool_name:
                continue

            # Log step execution
            with open(output_file, "a") as f:
                f.write(f"\n--- STEP {step_num}: {name} ---\n")
                f.write(f"Tool: {tool_name}\n")
                f.write(f"Params: {json.dumps(params)}\n\n")

            # Directly execute the steps based on tool name
            try:
                result = None

                if tool_name == "list_ollama_models":
                    result = await list_ollama_models()
                elif tool_name == "run_ollama_prompt":
                    result = await run_ollama_prompt(**params)
                elif tool_name == "get_job_status":
                    result = await get_job_status(**params)
                elif tool_name == "cancel_job":
                    result = await cancel_job(**params)
                elif tool_name == "list_jobs":
                    result = await list_jobs(**params if params else {})
                elif tool_name == "save_script":
                    result = await save_script(**params)
                elif tool_name == "list_scripts":
                    result = await list_scripts(**params if params else {})
                elif tool_name == "get_script":
                    result = await get_script(**params)
                elif tool_name == "run_script":
                    result = await run_script(**params)
                elif tool_name == "run_bash_command":
                    result = await run_bash_command(**params)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                # Record the result
                with open(output_file, "a") as f:
                    f.write(f"Result: {json.dumps(result)}\n")

                results.append({
                    "step": step_num,
                    "name": name,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                error_msg = f"ERROR executing {tool_name}: {str(e)}"
                with open(output_file, "a") as f:
                    f.write(f"{error_msg}\n")

                results.append({
                    "step": step_num,
                    "name": name,
                    "status": "error",
                    "message": error_msg
                })

        # Mark workflow as complete
        with open(output_file, "a") as f:
            f.write("\n--- WORKFLOW COMPLETED ---\n")

        return results

    # Start the workflow execution
    if wait_for_completion:
        try:
            results = await execute_workflow()
            return {
                "status": "complete",
                "run_id": run_id,
                "output_file": str(output_file),
                "results": results
            }
        except Exception as e:
            return {
                "status": "error",
                "run_id": run_id,
                "output_file": str(output_file),
                "message": f"Workflow execution failed: {str(e)}"
            }
    else:
        # Start the workflow in the background
        asyncio.create_task(execute_workflow())

        return {
            "status": "running",
            "run_id": run_id,
            "output_file": str(output_file),
            "message": "Workflow started, check output file for progress"
        }
