#!/usr/bin/env python
"""
Simple Chain Workflow for Ollama MCP

This script demonstrates a chain workflow using Ollama models without
relying on fast-agent. It implements a researcher → summarizer pipeline
that passes information between models sequentially.
"""

import argparse
import asyncio
import json
import os
import time
from pathlib import Path

# Set the output directory
OUTPUT_DIR = Path("/home/ty/Repositories/ai_workspace/ollama-mcp-server/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


async def run_ollama_prompt(model, prompt, system_prompt=None, temperature=0.6, wait_for_result=True):
    """Run a prompt with an Ollama model and return the result."""
    import subprocess
    import json

    cmd = [
        "uv", "run", "-m", "src.ollama_mcp_server.server",
        "--function", "run_ollama_prompt",
        "--args", json.dumps({
            "model": model,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "wait_for_result": wait_for_result
        })
    ]

    # Run in the parent directory of the script
    parent_dir = Path(os.path.abspath(__file__)).parent.parent

    result = subprocess.run(
        cmd,
        cwd=str(parent_dir),
        capture_output=True,
        text=True,
        check=True
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to parse response", "raw_output": result.stdout}


async def get_job_status(job_id):
    """Get the status of a job."""
    import subprocess
    import json

    cmd = [
        "uv", "run", "-m", "src.ollama_mcp_server.server",
        "--function", "get_job_status",
        "--args", json.dumps({"job_id": job_id})
    ]

    # Run in the parent directory of the script
    parent_dir = Path(os.path.abspath(__file__)).parent.parent

    result = subprocess.run(
        cmd,
        cwd=str(parent_dir),
        capture_output=True,
        text=True,
        check=True
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to parse response", "raw_output": result.stdout}


async def wait_for_job_completion(job_id, check_interval=1.0, max_wait=300):
    """Wait for a job to complete and return the result."""
    start_time = time.time()

    while time.time() - start_time < max_wait:
        job_status = await get_job_status(job_id)

        if job_status["status"] == "complete":
            return job_status
        elif job_status["status"] == "error":
            return job_status

        await asyncio.sleep(check_interval)

    return {"status": "timeout", "message": f"Job did not complete within {max_wait} seconds"}


async def extract_model_response(job_data):
    """Extract the model's response from job data."""
    if job_data["status"] == "complete":
        try:
            # For models that return JSON responses
            if "content" in job_data and job_data["content"]:
                if isinstance(job_data["content"], str):
                    # Try to find JSON in the response
                    content = job_data["content"]
                    try:
                        # Look for JSON objects in the content
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            response_data = json.loads(json_content)
                            if "response" in response_data:
                                return response_data["response"]
                            elif "final" in response_data:
                                return response_data["final"]
                            return json.dumps(response_data)
                    except json.JSONDecodeError:
                        pass

                    # If no JSON found, look for "RESPONSE:" section
                    response_marker = "RESPONSE:"
                    if response_marker in content:
                        response_section = content.split(response_marker)[1].strip()
                        # Clean up any ANSI escape sequences and control characters
                        import re
                        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                        response_section = ansi_escape.sub('', response_section)
                        return response_section

                    return content

            # Try to read the output file directly
            if "output_file" in job_data and os.path.exists(job_data["output_file"]):
                with open(job_data["output_file"], "r") as f:
                    content = f.read()
                    # Extract content after "RESPONSE:" if it exists
                    if "RESPONSE:" in content:
                        response_section = content.split("RESPONSE:")[1].strip()
                        # Clean up response
                        import re
                        # Remove ANSI escape sequences
                        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                        response_section = ansi_escape.sub('', response_section)
                        # Remove spinner characters
                        response_section = re.sub(r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', response_section)
                        # Clean up any JSON fragments
                        try:
                            json_start = response_section.find('{')
                            json_end = response_section.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_content = response_section[json_start:json_end]
                                response_data = json.loads(json_content)
                                if "response" in response_data:
                                    return response_data["response"]
                                elif "final" in response_data:
                                    return response_data["final"]
                                return json.dumps(response_data)
                        except (json.JSONDecodeError, ValueError):
                            pass

                        return response_section.strip()
                    return content
        except Exception as e:
            return f"Error extracting response: {str(e)}"

    return f"Job not complete: {job_data['status']}"


async def chain_workflow(query, researcher_model="generic.qwen3:30b-a3b",
                         summarizer_model="generic.qwen3", temperature=0.6):
    """Run a chain workflow with a researcher and summarizer."""
    print(f"🔍 Running chain workflow on: {query}")
    print(f"📚 Researcher model: {researcher_model}")
    print(f"📝 Summarizer model: {summarizer_model}")

    # Step 1: Run the researcher
    researcher_prompt = f"""
    You are a thorough researcher. Analyze the following topic in depth, providing comprehensive information.
    Your analysis should be detailed and well-structured.

    TOPIC: {query}

    Provide a research analysis with key insights, facts, applications, limitations, and supporting information.
    """

    print("\n🔍 Step 1: Running researcher analysis...")
    researcher_job = await run_ollama_prompt(
        model=researcher_model,
        prompt=researcher_prompt,
        system_prompt="You are a comprehensive researcher that provides detailed, factual analysis.",
        temperature=temperature,
        wait_for_result=False
    )

    if researcher_job["status"] == "running":
        print(f"✓ Researcher job started with ID: {researcher_job['job_id']}")
        researcher_result = await wait_for_job_completion(researcher_job["job_id"])
        researcher_response = await extract_model_response(researcher_result)
        print(f"\n✓ Researcher analysis complete ({len(researcher_response)} chars)")
    else:
        print(f"❌ Failed to start researcher job: {researcher_job['status']}")
        return

    # Step 2: Run the summarizer
    summarizer_prompt = f"""
    You are a concise summarizer. Take the following detailed research and create a clear, brief summary.
    Focus on the key points and insights, and organize them into a structured format.

    DETAILED RESEARCH:
    {researcher_response}

    Create a concise summary that highlights the most important points about this topic.
    """

    print("\n📝 Step 2: Running summarizer...")
    summarizer_job = await run_ollama_prompt(
        model=summarizer_model,
        prompt=summarizer_prompt,
        system_prompt="You are a concise summarizer that creates clear, structured summaries of complex information.",
        temperature=temperature,
        wait_for_result=False
    )

    if summarizer_job["status"] == "running":
        print(f"✓ Summarizer job started with ID: {summarizer_job['job_id']}")
        summarizer_result = await wait_for_job_completion(summarizer_job["job_id"])
        summarizer_response = await extract_model_response(summarizer_result)
        print(f"\n✓ Summarization complete ({len(summarizer_response)} chars)")
    else:
        print(f"❌ Failed to start summarizer job: {summarizer_job['status']}")
        return

    # Step 3: Create the final output
    workflow_id = f"chain_{int(time.time())}"
    output_file = OUTPUT_DIR / f"{workflow_id}.txt"

    with open(output_file, "w") as f:
        f.write("# Chain Workflow Results\n\n")
        f.write(f"## Query\n{query}\n\n")
        f.write(f"## Researcher Analysis ({researcher_model})\n\n{researcher_response}\n\n")
        f.write(f"## Summary ({summarizer_model})\n\n{summarizer_response}\n\n")

    print(f"\n✅ Chain workflow complete! Results saved to {output_file}")

    return {
        "workflow_id": workflow_id,
        "output_file": str(output_file),
        "query": query,
        "researcher_model": researcher_model,
        "summarizer_model": summarizer_model,
        "researcher_response": researcher_response,
        "summary": summarizer_response
    }


async def main():
    parser = argparse.ArgumentParser(description="Run a chain workflow with Ollama models")
    parser.add_argument("--query", type=str, required=True, help="The query to analyze")
    parser.add_argument("--researcher", type=str, default="qwen3:30b-a3b", help="Model for research phase")
    parser.add_argument("--summarizer", type=str, default="qwen3", help="Model for summarization phase")
    parser.add_argument("--temperature", type=float, default=0.6, help="Temperature for both models")

    args = parser.parse_args()

    result = await chain_workflow(
        query=args.query,
        researcher_model=args.researcher,
        summarizer_model=args.summarizer,
        temperature=args.temperature
    )

    if result:
        print("\n## Summary Output:")
        print(result["summary"])
        print(f"\nFull results available in: {result['output_file']}")


if __name__ == "__main__":
    asyncio.run(main())
