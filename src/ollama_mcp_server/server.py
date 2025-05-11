#!/usr/bin/env python
"""
Ollama MCP Server

Provides an MCP server interface for running Ollama models asynchronously.
Includes fast-agent integration for advanced agent workflows.
"""

import asyncio
import importlib.util
import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize paths relative to the project root using env var if available
if os.environ.get("OLLAMA_MCP_ROOT"):
    # Use the environment variable if set
    BASE_DIR = Path(os.environ["OLLAMA_MCP_ROOT"])
else:
    # Fall back to detecting from script location - go up two levels to reach repo root
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

# Print the actual paths for debugging
print(f"BASE_DIR: {BASE_DIR}")

# Define output directories
OUTPUTS_DIR = BASE_DIR / "outputs"
SCRIPTS_DIR = BASE_DIR / "scripts"
WORKFLOWS_DIR = BASE_DIR / "workflows"
FASTAGENT_DIR = BASE_DIR / "fast-agent-scripts"

# Print the actual paths for debugging
print(f"OUTPUTS_DIR: {OUTPUTS_DIR}")
print(f"SCRIPTS_DIR: {SCRIPTS_DIR}")
print(f"WORKFLOWS_DIR: {WORKFLOWS_DIR}")
print(f"FASTAGENT_DIR: {FASTAGENT_DIR}")

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)
WORKFLOWS_DIR.mkdir(exist_ok=True)
FASTAGENT_DIR.mkdir(exist_ok=True)

# We don't need to create a FastAgent config - the MCP server provides all functionality directly
# Fast-agent scripts can work with the MCP server tools without additional configuration

# Initialize the MCP server
mcp = FastMCP("OllamaMCPServer")

# Log the output paths for debugging
print(f"Using outputs directory: {OUTPUTS_DIR}")
print(f"Using scripts directory: {SCRIPTS_DIR}")
print(f"Using workflows directory: {WORKFLOWS_DIR}")

# Global instance for accessing server in prompt handlers
server_instance = None

# Dictionary to track running processes
running_processes: Dict[str, subprocess.Popen] = {}

# Dictionary to store process output for async handling
process_outputs: Dict[str, str] = {}

# Store the selected default Ollama model
default_ollama_model: Optional[str] = None


def clean_ansi_escape_codes(text: str) -> str:
    """
    Clean ANSI escape sequences and terminal control codes from text.

    Args:
        text: Text containing ANSI escape sequences

    Returns:
        Cleaned text without ANSI codes
    """
    if not text:
        return text

    # Pattern for ANSI escape sequences - covers color codes and cursor movement
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Remove ANSI escape sequences
    cleaned_text = ansi_pattern.sub('', text)

    # Additional cleanup for other control sequences
    # Remove cursor hide/show sequences
    cleaned_text = re.sub(r'\x1B\[\?25[hl]', '', cleaned_text)

    # Remove console mode sequences
    cleaned_text = re.sub(r'\x1B\[\?2026[hl]', '', cleaned_text)

    # Remove cursor position commands
    cleaned_text = re.sub(r'\x1B\[\d*G', '', cleaned_text)

    # Remove line clear commands
    cleaned_text = re.sub(r'\x1B\[\d*K', '', cleaned_text)

    # Clean up any line noise from cursor movement
    cleaned_text = re.sub(r'\r(?!\n)', '\n', cleaned_text)

    # Remove Unicode braille pattern characters often used for spinners
    cleaned_text = re.sub(r'[\u2800-\u28FF]', '', cleaned_text)

    # Normalize multiple consecutive newlines to max two
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    # Remove any whitespace-only lines
    cleaned_text = re.sub(r'\n[ \t]*\n', '\n\n', cleaned_text)

    # Trim leading/trailing whitespace
    cleaned_text = cleaned_text.strip()

    return cleaned_text


def clean_ollama_output(content: str) -> str:
    """
    Clean the output from an Ollama model, preserving metadata and prompt.

    Args:
        content: Raw content from the output file

    Returns:
        Cleaned content with ANSI codes removed and JSON properly parsed
    """
    if not content:
        return content

    # Check if this is an Ollama response
    if "RESPONSE:" in content:
        # Split into metadata/prompt and response
        parts = content.split("RESPONSE:", 1)
        header = parts[0] + "RESPONSE:\n"
        response_text = parts[1]

        # Check if the response might contain JSON
        try:
            # Try to parse each line as JSON
            response_lines = response_text.strip().split('\n')
            actual_response = ""

            for line in response_lines:
                line = line.strip()
                if not line:
                    continue

                # Skip download progress lines
                if "pulling" in line.lower() or "verifying" in line.lower() or "writing manifest" in line.lower() or "success" in line:
                    continue
                # Skip UI elements and token markers
                if line.startswith(("r", "[", "╭", "│", "╰")):
                    continue
                if any(char in line for char in ["⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]):
                    continue
                if line.startswith("METADATA:") or line.startswith("PROMPT:"):
                    continue

                try:
                    json_data = json.loads(line)
                    if "response" in json_data:
                        actual_response += json_data["response"]
                except json.JSONDecodeError:
                    # Not JSON, but might be actual response text
                    # Skip lines that look like token identifiers
                    if not re.match(r'^[a-z]\d+', line):
                        actual_response += line + "\n"

            if actual_response:
                # If we successfully extracted response data, use it
                cleaned_response = clean_ansi_escape_codes(actual_response)
                return header + cleaned_response
            
            # If we couldn't extract a clean response, try a different approach
            # Look for the [ASSISTANT] marker and extract text after it
            if "[ASSISTANT]" in response_text:
                assistant_parts = response_text.split("[ASSISTANT]", 1)
                if len(assistant_parts) > 1:
                    assistant_response = assistant_parts[1].strip()
                    # Remove any remaining UI elements
                    cleaned_response = re.sub(r'\[.*?\]', '', assistant_response)
                    cleaned_response = clean_ansi_escape_codes(cleaned_response)
                    return header + cleaned_response
                    
        except Exception:
            # Fall back to original cleaning if JSON parsing fails
            pass

        # Clean the response text (fallback)
        cleaned_response = clean_ansi_escape_codes(response_text)

        # Final attempt to extract only the meaningful content
        # Remove token markers and UI elements
        cleaned_response = re.sub(r'r\d+[a-z]*', '', cleaned_response)
        cleaned_response = re.sub(r'\[[^\]]+\]', '', cleaned_response)
        cleaned_response = re.sub(r'[╭│╰─]', '', cleaned_response)
        cleaned_response = re.sub(r'[⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', cleaned_response)
        
        # Reconstruct the content
        return header + cleaned_response

    # If not a typical Ollama response, return as is
    return content


@mcp.tool()
async def list_ollama_models() -> Dict[str, Any]:
    """List all available Ollama models - Shows installed models with correct names and sizes"""
    try:
        process = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        lines = process.stdout.strip().split('\n')
        models = []

        # Skip header line
        if len(lines) > 1:
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        models.append({
                            "name": parts[0],
                            "id": parts[1],
                            "size": parts[2]
                        })

        return {
            "status": "success",
            "models": models
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Failed to list Ollama models: {e.stderr}"
        }


@mcp.tool()
async def run_ollama_prompt(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    wait_for_result: bool = False,
    max_tokens: Optional[int] = None,
    output_format: str = "text"
) -> Dict[str, Any]:
    """Run a prompt with Ollama model - Execute prompts with specified models synchronously or asynchronously"""
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    output_file = OUTPUTS_DIR / f"{job_id}.txt"

    # Prepare the Ollama command
    cmd = ["ollama", "run", model, "--format", "json"]

    # Prepare the input JSON
    ollama_input = {
        "prompt": prompt,
        "stream": True,
        "temperature": temperature
    }

    if system_prompt:
        ollama_input["system"] = system_prompt

    if max_tokens:
        ollama_input["num_predict"] = max_tokens

    if output_format == "json":
        ollama_input["format"] = "json"

    # Write metadata at the top of the output file
    with open(output_file, "w") as f:
        metadata = {
            "job_id": job_id,
            "model": model,
            "timestamp": time.time(),
            "parameters": {
                "temperature": temperature,
                "system_prompt": system_prompt,
                "max_tokens": max_tokens,
                "output_format": output_format
            }
        }
        f.write(f"METADATA: {json.dumps(metadata)}\n\n")
        f.write(f"PROMPT: {prompt}\n\n")
        f.write("RESPONSE:\n")

    # Run the process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Send the input to the model
    if process.stdin:
        process.stdin.write(json.dumps(ollama_input) + "\n")
        process.stdin.close()

    # Create and run a background task to capture output
    async def capture_output():
        output = ""
        response_text = ""
        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                
                output += line + "\n"
                
                # Process JSON output if available
                try:
                    json_data = json.loads(line)
                    if "response" in json_data:
                        response_text += json_data["response"]
                        # Append the processed response to the file in real-time
                        with open(output_file, "a") as f:
                            f.write(json_data["response"])
                except json.JSONDecodeError:
                    # Skip download progress, UI elements and token data
                    if "pulling" in line.lower() or "verifying" in line.lower() or "writing manifest" in line.lower() or "success" in line:
                        # Skip download progress lines
                        continue
                    if not line.startswith(("r", "[", "╭", "│", "╰")) and not ("⠙" in line or "⠹" in line or "⠸" in line or "⠼" in line or "⠴" in line or "⠦" in line or "⠧" in line or "⠇" in line or "⠏" in line):
                        # This might be actual response text
                        if line and not line.startswith("METADATA:") and not line.startswith("PROMPT:"):
                            with open(output_file, "a") as f:
                                f.write(line + "\n")

        # Store the complete output
        process_outputs[job_id] = response_text or output

        # Wait for the process to finish
        process.wait()

    # Start the background task to capture output without waiting
    asyncio.create_task(capture_output())

    # Store the process for management
    running_processes[job_id] = process

    # If wait_for_result is True, wait for the process to complete
    if wait_for_result:
        await asyncio.to_thread(process.wait)

        # Check process status
        if process.returncode == 0:
            try:
                with open(output_file, "r") as f:
                    content = f.read()

                # Clean up the process
                if job_id in running_processes:
                    del running_processes[job_id]

                # Clean the output
                content = clean_ollama_output(content)

                return {
                    "status": "complete",
                    "job_id": job_id,
                    "output_file": str(output_file),
                    "content": content
                }
            except Exception as e:
                return {
                    "status": "error",
                    "job_id": job_id,
                    "message": f"Error reading output: {str(e)}"
                }
        else:
            return {
                "status": "error",
                "job_id": job_id,
                "message": f"Process exited with code {process.returncode}"
            }

    # Return immediately with job information
    return {
        "status": "running",
        "job_id": job_id,
        "output_file": str(output_file),
        "message": "Process started, check job status for completion"
    }


@mcp.tool()
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Check the status of a specific job by its ID.

    Args:
        job_id: The ID of the job to check

    Returns:
        Dict with job status information and content if complete
    """
    output_file = OUTPUTS_DIR / f"{job_id}.txt"

    if not output_file.exists():
        return {
            "status": "not_found",
            "message": f"No job found with ID {job_id}"
        }

    # Check if the process is still running
    process = running_processes.get(job_id)
    if process and process.poll() is None:
        return {
            "status": "running",
            "job_id": job_id,
            "output_file": str(output_file)
        }

    # Read the output file
    try:
        with open(output_file, "r") as f:
            content = f.read()

        # Clean the output if it's not a bash command
        if "_bash.txt" not in str(output_file):
            content = clean_ollama_output(content)

    except Exception as e:
        return {
            "status": "error",
            "job_id": job_id,
            "message": f"Error reading output file: {str(e)}"
        }

    # Process is complete, clean up if needed
    if job_id in running_processes:
        del running_processes[job_id]

    return {
        "status": "complete",
        "job_id": job_id,
        "output_file": str(output_file),
        "content": content
    }

@mcp.tool()
async def list_jobs() -> Dict[str, Any]:
    """
    List all jobs - both running and completed.

    Returns:
        Dict with lists of running and completed jobs
    """
    # Check running processes
    running_jobs = []
    for job_id, process in list(running_processes.items()):
        # Update status and clean up completed processes
        if process.poll() is not None:
            del running_processes[job_id]
        else:
            running_jobs.append(job_id)

    # List output files to find completed jobs
    completed_jobs = []
    for output_file in OUTPUTS_DIR.glob("*.txt"):
        job_id = output_file.stem
        if job_id not in running_jobs:
            # Get metadata if available
            try:
                with open(output_file, "r") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("METADATA:"):
                        metadata = json.loads(first_line[9:])
                        completed_jobs.append({
                            "job_id": job_id,
                            "output_file": str(output_file),
                            "timestamp": metadata.get("timestamp"),
                            "model": metadata.get("model")
                        })
                    else:
                        completed_jobs.append({
                            "job_id": job_id,
                            "output_file": str(output_file),
                            "timestamp": output_file.stat().st_mtime
                        })
            except (IOError, json.JSONDecodeError):
                # Fall back to file stats if metadata parsing fails
                completed_jobs.append({
                    "job_id": job_id,
                    "output_file": str(output_file),
                    "timestamp": output_file.stat().st_mtime
                })

    # Sort completed jobs by timestamp, newest first
    completed_jobs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    return {
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs
    }

@mcp.tool()
async def cancel_job(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running job by its ID.

    Args:
        job_id: The ID of the job to cancel

    Returns:
        Dict with cancellation status
    """
    process = running_processes.get(job_id)

    if not process:
        return {
            "status": "not_found",
            "message": f"No running process found with ID {job_id}"
        }

    if process.poll() is None:
        # Process is still running, terminate it
        process.terminate()
        try:
            # Wait a bit for graceful termination
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate gracefully
            process.kill()

        # Update output file with cancellation notice
        output_file = OUTPUTS_DIR / f"{job_id}.txt"
        if output_file.exists():
            try:
                with open(output_file, "a") as f:
                    f.write("\n\n[JOB CANCELLED BY USER]\n")
            except IOError:
                pass

        # Clean up references
        del running_processes[job_id]

        return {
            "status": "cancelled",
            "job_id": job_id,
            "message": "Process has been terminated"
        }
    else:
        # Process has already completed
        if job_id in running_processes:
            del running_processes[job_id]

        return {
            "status": "already_complete",
            "job_id": job_id,
            "message": "Process had already completed"
        }

@mcp.tool()
async def save_script(
    name: str,
    content: str
) -> Dict[str, Any]:
    """
    Save a script template to the scripts directory.

    Args:
        name: Name for the script (without extension)
        content: Content of the script

    Returns:
        Dict with save status
    """
    script_path = SCRIPTS_DIR / f"{name}.txt"

    try:
        with open(script_path, "w") as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Script saved successfully as {name}.txt",
            "path": str(script_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save script: {str(e)}"
        }


@mcp.tool()
async def list_scripts() -> Dict[str, Any]:
    """
    List all available scripts in the scripts directory.

    Returns:
        Dict with list of scripts and their metadata
    """
    scripts = []

    for script_file in SCRIPTS_DIR.glob("*.txt"):
        try:
            # Read the first few lines for preview
            with open(script_file, "r") as f:
                content = f.read(500)  # First 500 chars
                preview = content if len(content) < 100 else content[:97] + "..."
        except Exception:
            preview = "[Error reading file]"

        scripts.append({
            "name": script_file.stem,
            "path": str(script_file),
            "modified_at": script_file.stat().st_mtime,
            "preview": preview
        })

    # Sort by last modified time, newest first
    scripts.sort(key=lambda x: x["modified_at"], reverse=True)

    return {
        "scripts": scripts
    }

@mcp.tool()
async def get_script(name: str) -> Dict[str, Any]:
    """
    Get the content of a script by name.

    Args:
        name: Name of the script (without extension)

    Returns:
        Dict with script content and metadata
    """
    script_path = SCRIPTS_DIR / f"{name}.txt"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.txt' not found"
        }

    try:
        with open(script_path, "r") as f:
            content = f.read()

        return {
            "status": "success",
            "name": name,
            "path": str(script_path),
            "content": content,
            "modified_at": script_path.stat().st_mtime
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read script: {str(e)}"
        }


@mcp.tool()
async def run_script(
    script_name: str,
    model: str,
    variables: Optional[Dict[str, str]] = None,
    temperature: float = 0.7,
    wait_for_result: bool = False,
    max_tokens: Optional[int] = None,
    output_format: str = "text"
) -> Dict[str, Any]:
    """
    Run a script template with variable substitution.

    Args:
        script_name: Name of the script to run (without extension)
        model: Name of the Ollama model to use
        variables: Dictionary of variables to substitute in the script
        temperature: Sampling temperature (0.0 to 1.0)
        wait_for_result: Whether to wait for completion before returning
        max_tokens: Maximum number of tokens to generate
        output_format: Output format: "text" or "json"

    Returns:
        Dict with job status information
    """
    script_path = SCRIPTS_DIR / f"{script_name}.txt"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{script_name}.txt' not found"
        }

    try:
        # Read the script content
        with open(script_path, "r") as f:
            content = f.read()

        # Substitute variables if provided
        if variables:
            for key, value in variables.items():
                placeholder = "{" + key + "}"
                content = content.replace(placeholder, value)

        # Check for system prompt (format: "SYSTEM: <system prompt>")
        system_prompt = None
        prompt = content

        if content.startswith("SYSTEM:"):
            lines = content.split("\n", 1)
            if len(lines) > 1:
                system_line = lines[0].strip()
                system_prompt = system_line[7:].strip()  # Remove "SYSTEM: " prefix
                prompt = lines[1].strip()

        # Run the prompt
        return await run_ollama_prompt(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            wait_for_result=wait_for_result,
            max_tokens=max_tokens,
            output_format=output_format
        )
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to run script: {str(e)}"
        }


@mcp.tool()
async def run_bash_command(
    command: str,
    wait_for_result: bool = False,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run a bash command and capture its output.

    Args:
        command: The bash command to execute
        wait_for_result: Whether to wait for completion before returning
        timeout: Maximum time (in seconds) to wait for the command to complete

    Returns:
        Dict with command status information
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    output_file = OUTPUTS_DIR / f"{job_id}_bash.txt"

    # Write metadata to the output file
    with open(output_file, "w") as f:
        metadata = {
            "job_id": job_id,
            "command": command,
            "timestamp": time.time()
        }
        f.write(f"METADATA: {json.dumps(metadata)}\n\n")
        f.write(f"COMMAND: {command}\n\n")
        f.write("OUTPUT:\n")

    # Run the command
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Create and run a background task to capture output
    async def capture_output():
        output = ""
        if process.stdout:
            for line in process.stdout:
                output += line
                # Append the output to the file in real-time
                with open(output_file, "a") as f:
                    f.write(line)

        # Store the complete output
        process_outputs[job_id] = output

        # Wait for the process to finish
        process.wait()

    # Start the background task to capture output without waiting
    asyncio.create_task(capture_output())

    # Store the process for management
    running_processes[job_id] = process

    # If wait_for_result is True, wait for the process to complete
    if wait_for_result:
        try:
            if timeout:
                await asyncio.wait_for(asyncio.to_thread(process.wait), timeout=timeout)
            else:
                await asyncio.to_thread(process.wait)

            # Read the output file
            with open(output_file, "r") as f:
                content = f.read()

            # Clean up the process
            if job_id in running_processes:
                del running_processes[job_id]

            return {
                "status": "complete",
                "job_id": job_id,
                "output_file": str(output_file),
                "exitcode": process.returncode,
                "content": content
            }
        except asyncio.TimeoutError:
            # Timeout occurred, terminate the process
            process.terminate()
            return {
                "status": "timeout",
                "job_id": job_id,
                "output_file": str(output_file),
                "message": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "job_id": job_id,
                "message": f"Error: {str(e)}"
            }

    # Return immediately with job information
    return {
        "status": "running",
        "job_id": job_id,
        "output_file": str(output_file),
        "message": "Command started, check job status for completion"
    }


# This is our fix to properly handle nested functions in the workflow tool
@mcp.tool()
async def run_workflow(
    steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run a workflow of multiple steps sequentially.

    Args:
        steps: List of step dictionaries, each containing:
               - tool: Name of the tool to call (e.g., "run_ollama_prompt")
               - params: Parameters to pass to the tool
               - name: Optional step name

    Returns:
        Dict with workflow execution status
    """
    # Generate a unique workflow run ID
    run_id = str(uuid.uuid4())
    output_file = OUTPUTS_DIR / f"{run_id}_workflow.txt"

    # Write metadata to the output file
    with open(output_file, "w") as f:
        metadata = {
            "run_id": run_id,
            "started_at": time.time(),
            "steps_count": len(steps),
            "current_dir": os.getcwd()
        }
        f.write(f"WORKFLOW RUN: {json.dumps(metadata)}\n\n")
        f.write(f"OUTPUT DIR: {OUTPUTS_DIR}\n")
        f.write(f"SCRIPTS DIR: {SCRIPTS_DIR}\n")
        f.write(f"WORKFLOWS DIR: {WORKFLOWS_DIR}\n\n")

    # Function to execute the workflow steps
    async def execute_workflow():
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

            # Remove any wait_for_result parameters to ensure consistent behavior
            if "wait_for_result" in params:
                del params["wait_for_result"]

            # Execute the tool using MCP server's function registry 
            # instead of hardcoding each tool
            try:
                # Get the actual tool function from MCP registry
                tool_fn = getattr(mcp._func_registry, tool_name, None)
                
                if tool_fn is None:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                # Execute the tool with its parameters
                result = await tool_fn(**params)
                
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

    # Start the workflow in the background
    asyncio.create_task(execute_workflow())

    return {
        "status": "running",
        "run_id": run_id,
        "output_file": str(output_file),
        "message": "Workflow started, check output file for progress"
    }


# ---------- Fast Agent Tools ----------

@mcp.tool()
async def list_fastagent_scripts() -> Dict[str, Any]:
    """
    List all available fast-agent scripts in the fast-agent-scripts directory.

    Returns:
        Dict with list of scripts and their metadata
    """
    scripts = []

    try:
        # List all Python scripts in the fast-agent-scripts directory
        for script_file in FASTAGENT_DIR.glob("*.py"):
            if script_file.name == "__init__.py":
                continue

            # Try to get the docstring from the script
            try:
                spec = importlib.util.spec_from_file_location("module.name", script_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    docstring = module.__doc__ or "No description available"
                else:
                    docstring = "Unable to load module"
            except Exception:
                docstring = "Error reading script"

            scripts.append({
                "name": script_file.stem,
                "path": str(script_file),
                "modified_at": script_file.stat().st_mtime,
                "description": docstring
            })

        # Sort by name
        scripts.sort(key=lambda x: x["name"])

        return {
            "status": "success",
            "scripts": scripts
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing fast-agent scripts: {str(e)}"
        }


@mcp.tool()
async def create_fastagent_script(
    name: str,
    script_type: str = "basic",
    instruction: str = "You are a helpful assistant",
    use_ollama: bool = True,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new fast-agent script with the specified parameters.

    Args:
        name: Name for the script (without extension)
        script_type: Type of script to create ("basic", "workflow", "chain", "parallel", "router")
        instruction: Base instruction for the agent
        use_ollama: Whether to use the Ollama MCP server

    Returns:
        Dict with creation status and script info
    """
    script_path = FASTAGENT_DIR / f"{name}.py"

    # Check if script already exists
    if script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.py' already exists"
        }

    # Generate the script content based on type
    if script_type == "basic":
        # Prepare model configuration part
        model_config = f'    model="{model}",' if model else ""

        content = f'''#!/usr/bin/env python
"""
Basic Fast-Agent example: {name}
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("{name.title()} Agent")

@fast.agent(
    name="{name}_agent",
    instruction="{instruction}",{model_config}
    servers=[{"ollama_server" if use_ollama else ""}]
)
async def main():
    # Run the agent
    async with fast.run() as agent:
        # Start interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
'''
    elif script_type == "workflow":
        # Prepare model configuration part
        model_config = f'    model="{model}",' if model else ""

        content = f'''#!/usr/bin/env python
"""
Workflow Fast-Agent example: {name}
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("{name.title()} Agent")

@fast.agent(
    name="researcher",
    instruction="You research topics thoroughly and provide detailed information.",{model_config}
    servers=[{"ollama_server" if use_ollama else ""}]
)

@fast.agent(
    name="summarizer",
    instruction="You take complex information and summarize it concisely.",{model_config}
    servers=[{"ollama_server" if use_ollama else ""}]
)

@fast.chain(
    name="{name}_workflow",
    sequence=["researcher", "summarizer"],
    instruction="{instruction}"
)

async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
'''
    else:
        return {
            "status": "error",
            "message": f"Unsupported script type: {script_type}"
        }

    try:
        # Write the script file
        with open(script_path, "w") as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Script '{name}.py' created successfully",
            "path": str(script_path),
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create script: {str(e)}"
        }


@mcp.tool()
async def get_fastagent_script(name: str) -> Dict[str, Any]:
    """
    Get the content of a fast-agent script by name.

    Args:
        name: Name of the script (without extension)

    Returns:
        Dict with script content and metadata
    """
    script_path = FASTAGENT_DIR / f"{name}.py"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.py' not found"
        }

    try:
        with open(script_path, "r") as f:
            content = f.read()

        return {
            "status": "success",
            "name": name,
            "path": str(script_path),
            "content": content,
            "modified_at": script_path.stat().st_mtime
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read script: {str(e)}"
        }


@mcp.tool()
async def update_fastagent_script(
    name: str,
    content: str
) -> Dict[str, Any]:
    """
    Update an existing fast-agent script.

    Args:
        name: Name of the script (without extension)
        content: New content for the script

    Returns:
        Dict with update status
    """
    script_path = FASTAGENT_DIR / f"{name}.py"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.py' not found"
        }

    try:
        with open(script_path, "w") as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Script '{name}.py' updated successfully",
            "path": str(script_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to update script: {str(e)}"
        }


@mcp.tool()
async def delete_fastagent_script(name: str) -> Dict[str, Any]:
    """
    Delete a fast-agent script.

    Args:
        name: Name of the script (without extension)

    Returns:
        Dict with deletion status
    """
    script_path = FASTAGENT_DIR / f"{name}.py"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.py' not found"
        }

    try:
        script_path.unlink()

        return {
            "status": "success",
            "message": f"Script '{name}.py' deleted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete script: {str(e)}"
        }


@mcp.tool()
async def run_fastagent_script(
    name: str,
    agent_name: Optional[str] = None,
    message: Optional[str] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run a fast-agent script and optionally send a message to a specific agent.

    Args:
        name: Name of the script (without extension)
        agent_name: Optional name of the agent to target (defaults to the main agent)
        message: Optional message to send to the agent
        timeout: Maximum time (in seconds) to wait for the command to complete

    Returns:
        Dict with execution status
    """
    script_path = FASTAGENT_DIR / f"{name}.py"

    if not script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}.py' not found"
        }

    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    output_file = OUTPUTS_DIR / f"{job_id}_fastagent.txt"

    # Build the command
    cmd = ["uv", "run", str(script_path)]

    # Add agent name if specified
    if agent_name:
        cmd.extend(["--agent", agent_name])

    # Add message if specified
    if message:
        cmd.extend(["--message", message])

    # Add quiet mode to get cleaner output for programmatic use
    cmd.append("--quiet")

    # Write metadata to the output file
    with open(output_file, "w") as f:
        metadata = {
            "job_id": job_id,
            "script": name,
            "agent": agent_name,
            "message": message,
            "timestamp": time.time()
        }
        f.write(f"METADATA: {json.dumps(metadata)}\n\n")
        f.write(f"COMMAND: {' '.join(cmd)}\n\n")
        f.write("OUTPUT:\n")

    # Run the command
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Create and run a background task to capture output
    async def capture_output():
        output = ""
        if process.stdout:
            for line in process.stdout:
                output += line
                # Append the output to the file in real-time
                with open(output_file, "a") as f:
                    f.write(line)

        # Wait for the process to finish
        process.wait()

    # Start the background task to capture output without waiting
    asyncio.create_task(capture_output())

    # Store the process for management
    running_processes[job_id] = process

    # Return immediately with job information
    return {
        "status": "running",
        "job_id": job_id,
        "output_file": str(output_file),
        "message": "FastAgent script started, check job status for completion"
    }


@mcp.tool()
async def create_fastagent_workflow(
    name: str,
    agents: List[str],
    workflow_type: str = "chain",
    instruction: str = "Complete the workflow effectively"
) -> Dict[str, Any]:
    """
    Create a new fast-agent workflow script that connects multiple agents.

    Args:
        name: Name for the workflow script (without extension)
        agents: List of agent names to include in the workflow
        workflow_type: Type of workflow ("chain", "parallel", "router", "evaluator")
        instruction: Instruction that describes the workflow's purpose

    Returns:
        Dict with creation status and script info
    """
    script_path = FASTAGENT_DIR / f"{name}_workflow.py"

    # Check if script already exists
    if script_path.exists():
        return {
            "status": "error",
            "message": f"Script '{name}_workflow.py' already exists"
        }

    # Generate agent declarations
    agent_declarations = ""
    for i, agent_name in enumerate(agents):
        agent_declarations += f'''@fast.agent(
    name="{agent_name}",
    instruction="Agent {i+1} in the {name} workflow.",
    servers=["ollama_server"]
)

'''

    # Generate workflow declaration based on type
    if workflow_type == "chain":
        workflow_declaration = f'''@fast.chain(
    name="{name}_workflow",
    sequence={agents},
    instruction="{instruction}"
)
'''
    elif workflow_type == "parallel":
        workflow_declaration = f'''@fast.parallel(
    name="{name}_workflow",
    fan_out={agents},
    instruction="{instruction}"
)
'''
    elif workflow_type == "router":
        workflow_declaration = f'''@fast.router(
    name="{name}_workflow",
    agents={agents},
    instruction="{instruction}"
)
'''
    elif workflow_type == "evaluator":
        if len(agents) < 2:
            return {
                "status": "error",
                "message": "Evaluator workflow requires at least 2 agents"
            }
        workflow_declaration = f'''@fast.evaluator_optimizer(
    name="{name}_workflow",
    generator="{agents[0]}",
    evaluator="{agents[1]}",
    instruction="{instruction}",
    max_refinements=3
)
'''
    else:
        return {
            "status": "error",
            "message": f"Unsupported workflow type: {workflow_type}"
        }

    # Generate the full script content
    content = f'''#!/usr/bin/env python
"""
{workflow_type.title()} Workflow: {name}
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create FastAgent instance
fast = FastAgent("{name.title()} Workflow")

{agent_declarations}
{workflow_declaration}

async def main():
    async with fast.run() as agent:
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
'''

    try:
        # Write the script file
        with open(script_path, "w") as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Workflow script '{name}_workflow.py' created successfully",
            "path": str(script_path),
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create workflow script: {str(e)}"
        }


# ---------- MCP Prompts ----------

@mcp.prompt()
async def ollama_run_prompt(
    prompt: str,
    model: str = "qwen3:0.6b",
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    output_format: str = "text"
) -> str:
    """Run a prompt with specified Ollama model - Execute prompts with detailed parameter guidance"""
    
    # Model format guidance
    model_format_guide = f"""
MODEL FORMAT EXAMPLES:
- Standard: qwen3:0.6b, llama3:8b, mistral:7b
- Custom: your-model:tag
- With provider: provider/model:tag
CURRENT: {model}
"""
    
    # Output format options
    output_format_guide = f"""
OUTPUT FORMAT OPTIONS:
- text: Standard text response (default)
- json: Structured JSON output
SELECTED: {output_format}
"""
    
    return f"""Execute an Ollama model prompt using the MCP server tools.

TASK: Run the following prompt with the specified Ollama model.

PARAMETERS:
- PROMPT: {prompt}
- MODEL: {model}
- TEMPERATURE: {temperature} (0.0=deterministic, 1.0=creative)
- SYSTEM_PROMPT: {system_prompt or 'None'}
- MAX_TOKENS: {max_tokens or 'default'}
- OUTPUT_FORMAT: {output_format}

{model_format_guide}
{output_format_guide}

STEP-BY-STEP EXECUTION:

1. VALIDATE MODEL (if unsure):
   Tool: list_ollama_models
   Purpose: Verify model exists and get exact name
   Use when: Model name uncertain or getting errors

2. EXECUTE PROMPT:
   Tool: run_ollama_prompt
   Required Parameters:
   - model: "{model}"
   - prompt: "{prompt}"
   Optional Parameters:
   - system_prompt: {f'"{system_prompt}"' if system_prompt else 'null'}
   - temperature: {temperature}
   - max_tokens: {max_tokens if max_tokens else 'null'}  
   - output_format: "{output_format}"
   - wait_for_result: true (for immediate response)

3. HANDLE ASYNC EXECUTION (if wait_for_result=false):
   Tool: get_job_status
   Parameters:
   - job_id: (returned from run_ollama_prompt)
   Process:
   - Poll until status="complete"
   - Retrieve content from response

TOOLS WITH DESCRIPTIONS:
- list_ollama_models: List all installed Ollama models with exact names and sizes
- run_ollama_prompt: Execute a prompt with an Ollama model (sync or async)
- get_job_status: Check completion status and retrieve results for async jobs

ERROR HANDLING:
- "Model not found": Use list_ollama_models to find correct name
- "Invalid parameters": Check parameter format and types
- "Timeout": Increase timeout or use async execution"""


@mcp.prompt()
async def model_comparison(
    prompt: str,
    models: str,
    temperature: Optional[float] = 0.7
) -> str:
    """Compare responses from multiple models"""
    model_list = [m.strip() for m in models.split(',') if m.strip()]
    
    return f"""Compare responses from multiple Ollama models for the same prompt.

TASK: Run a prompt through multiple models and compare their outputs.

PROMPT: {prompt}
MODELS: {', '.join(model_list)}
TEMPERATURE: {temperature}

INSTRUCTIONS:
1. For each model in the list:
   a. Call 'run_ollama_prompt' with the same prompt
   b. Set wait_for_result=True to get immediate results
   c. Collect each model's response
2. Organize and compare the responses
3. Present a comparison highlighting differences and similarities

TOOLS TO USE:
- run_ollama_prompt: Execute prompt for each model
- list_ollama_models: Verify models are available
- get_job_status: Check job completion if needed"""


@mcp.prompt()
async def fast_agent_workflow(
    workflow_type: str,
    agent_names: str,
    initial_prompt: str,
    model: Optional[str] = "phi4-reasoning:14b-plus-q4_K_M"
) -> str:
    """Run a fast-agent workflow - Create and execute agent workflows with guided parameter selection"""
    agents = [a.strip() for a in agent_names.split(',') if a.strip()]
    
    # Validate workflow type
    valid_workflow_types = ["chain", "parallel", "router", "evaluator"]
    workflow_type_guidance = f"""
VALID WORKFLOW TYPES:
- chain: Sequential execution of agents
- parallel: Run agents simultaneously  
- router: Route to appropriate agent based on input
- evaluator: Iterative refinement with generator/evaluator pattern

SELECTED: {workflow_type}
{"⚠️ INVALID TYPE! Use one of: " + ', '.join(valid_workflow_types) if workflow_type not in valid_workflow_types else "✓ Valid workflow type"}
"""
    
    # Validate script type
    valid_script_types = ["basic", "workflow"]
    script_type_guidance = f"""
VALID SCRIPT TYPES for create_fastagent_script:
- basic: Single agent script
- workflow: Multi-agent workflow script

NOTE: For workflow_type '{workflow_type}', use create_fastagent_workflow instead of create_fastagent_script
"""
    
    return f"""Create and execute a fast-agent workflow using MCP tools.

TASK: Set up and run a {workflow_type} workflow with specified agents.

WORKFLOW_TYPE: {workflow_type}
AGENTS: {', '.join(agents)}
INITIAL_PROMPT: {initial_prompt}
DEFAULT_MODEL: {model}

{workflow_type_guidance}

STEP-BY-STEP INSTRUCTIONS:

1. VALIDATE MODEL (Optional):
   Tool: list_ollama_models
   Purpose: Verify model exists and get correct name format
   Example: Use if unsure about model name like "generic.model-name"

2. CREATE WORKFLOW:
   {script_type_guidance}
   
   For multi-agent workflows (recommended):
   Tool: create_fastagent_workflow
   Parameters:
   - name: Choose a descriptive name (e.g., "code_executor_workflow")
   - agents: {agents}
   - workflow_type: "{workflow_type}"
   - instruction: "{initial_prompt}"

3. EXECUTE WORKFLOW:
   Tool: run_fastagent_script
   Parameters:
   - name: Same as created workflow name
   - agent_name: Optional, defaults to first agent
   - message: Specific task to execute
   - timeout: Optional, default 300 seconds

4. MONITOR EXECUTION:
   Tool: get_job_status
   Parameters:
   - job_id: Returned from run_fastagent_script
   
5. CHECK RESULTS:
   Tool: get_job_status (when status is "complete")
   Returns: Full output content

TOOLS WITH DESCRIPTIONS:
- list_ollama_models: List all available Ollama models with correct names
- create_fastagent_script: Create single-agent scripts (types: basic, workflow)
- create_fastagent_workflow: Create multi-agent workflows (types: chain, parallel, router, evaluator)
- run_fastagent_script: Execute created scripts/workflows
- get_job_status: Check job status and retrieve output
- list_fastagent_scripts: View all available scripts

ERROR HANDLING:
- If "Unsupported script type": Use valid types listed above
- If "Script not found": Use exact name from creation step
- If "Model not found": Use list_ollama_models to find correct name"""


@mcp.prompt()
async def script_executor(
    script_name: str,
    model: str,
    variables: Optional[str] = None
) -> str:
    """Execute saved script template - Run scripts with variable substitution and validation"""
    var_dict = {}
    var_parse_error = None
    if variables:
        try:
            var_dict = json.loads(variables)
        except json.JSONDecodeError as e:
            var_parse_error = str(e)
            
    # Variable format guidance
    var_format_guide = f"""
VARIABLE FORMAT:
Expected: JSON object {{"key": "value", "key2": "value2"}}
Provided: {variables}
{f"⚠️ PARSE ERROR: {var_parse_error}" if var_parse_error else "✓ Valid JSON" if var_dict else "ℹ️ No variables provided"}
"""
    
    return f"""Execute a saved script template using MCP tools.

TASK: Run a saved script with variable substitution.

PARAMETERS:
- SCRIPT_NAME: {script_name}
- MODEL: {model}
- VARIABLES: {json.dumps(var_dict, indent=2) if var_dict else 'None'}

{var_format_guide}

STEP-BY-STEP EXECUTION:

1. VERIFY SCRIPT EXISTS:
   Tool: get_script
   Parameters:
   - name: "{script_name}"
   
   If Error: "Script not found"
   Then: Use list_scripts to see available options

2. LIST AVAILABLE SCRIPTS (if needed):
   Tool: list_scripts
   Purpose: Show all scripts with preview
   Action: Select correct script name

3. VALIDATE MODEL:
   Tool: list_ollama_models
   Purpose: Ensure model exists
   Use when: Model errors occur

4. EXECUTE SCRIPT:
   Tool: run_script
   Parameters:
   - script_name: "{script_name}"
   - model: "{model}"
   - variables: {json.dumps(var_dict) if var_dict else 'null'}
   - wait_for_result: false (for async execution)
   - temperature: 0.7 (optional)
   - max_tokens: null (optional)
   - output_format: "text" (optional)

5. MONITOR EXECUTION:
   Tool: get_job_status
   Parameters:
   - job_id: (returned from run_script)
   Process:
   - Poll periodically until status="complete"
   - Retrieve output content

6. HANDLE ERRORS:
   Common Issues:
   - "Script not found": Check exact name with list_scripts
   - "Invalid variables": Ensure valid JSON format
   - "Model not found": Verify with list_ollama_models

TOOLS WITH DESCRIPTIONS:
- get_script: Retrieve script content by name
- list_scripts: List all saved scripts with previews and metadata
- run_script: Execute a script with variable substitution
- get_job_status: Monitor job progress and retrieve results
- save_script: Create new script templates
- list_ollama_models: List available models with exact names

SCRIPT TEMPLATE SYNTAX:
Scripts support:
- Variable substitution: {{variable_name}}
- System prompts: SYSTEM: <prompt text>
- Direct prompts: Plain text after SYSTEM line"""


@mcp.prompt()
async def model_analysis(
    model: str,
    analysis_type: Optional[str] = "capabilities",
    test_prompts: Optional[str] = None
) -> str:
    """Analyze model capabilities and performance"""
    tests = []
    if test_prompts:
        tests = [p.strip() for p in test_prompts.split(',') if p.strip()]
        
    return f"""Analyze an Ollama model's capabilities and performance.

TASK: Conduct a {analysis_type} analysis on the specified model.

MODEL: {model}
ANALYSIS_TYPE: {analysis_type}
TEST_PROMPTS: {json.dumps(tests, indent=2) if tests else 'Default test suite'}

INSTRUCTIONS:
1. Verify model availability with 'list_ollama_models'
2. Run test prompts using 'run_ollama_prompt':
   - Test basic capabilities
   - Measure response times
   - Evaluate output quality
3. For each test prompt:
   - Execute with wait_for_result=True
   - Capture response time and quality
4. Compile analysis results
5. Generate summary report

TOOLS TO USE:
- list_ollama_models: Verify model exists
- run_ollama_prompt: Execute test prompts
- get_job_status: Monitor job completion
- run_workflow: For complex test sequences"""


@mcp.prompt()
async def iterative_refinement(
    initial_prompt: str,
    generator_model: str,
    evaluator_model: str,
    min_rating: Optional[str] = "GOOD",
    max_iterations: Optional[int] = 3
) -> str:
    """Iteratively refine output using evaluator pattern"""
    return f"""Implement an iterative refinement workflow using generator and evaluator models.

TASK: Refine output through evaluator-optimizer pattern.

INITIAL_PROMPT: {initial_prompt}
GENERATOR_MODEL: {generator_model}
EVALUATOR_MODEL: {evaluator_model}
MIN_RATING: {min_rating}
MAX_ITERATIONS: {max_iterations}

INSTRUCTIONS:
1. Create workflow with 'create_fastagent_workflow':
   - workflow_type: "evaluator"
   - agents: ["{generator_model}_agent", "{evaluator_model}_agent"]
2. Configure evaluator settings:
   - min_rating: "{min_rating}"
   - max_refinements: {max_iterations}
3. Execute workflow with 'run_fastagent_script'
4. Monitor iterations with 'get_job_status'
5. Return final refined output

TOOLS TO USE:
- create_fastagent_workflow: Set up evaluator-optimizer workflow
- run_fastagent_script: Execute the workflow
- get_job_status: Monitor progress
- run_ollama_prompt: For individual model calls if needed"""


@mcp.prompt()
async def batch_processing(
    prompts: str,
    model: str,
    parallel: Optional[bool] = False,
    output_format: Optional[str] = "text"
) -> str:
    """Process multiple prompts in batch"""
    prompt_list = []
    try:
        prompt_list = json.loads(prompts)
    except json.JSONDecodeError:
        pass
        
    return f"""Process multiple prompts in batch using Ollama models.

TASK: Execute batch processing of multiple prompts.

PROMPTS: {json.dumps(prompt_list, indent=2) if prompt_list else 'Invalid JSON - check format'}
MODEL: {model}
PARALLEL: {parallel}
OUTPUT_FORMAT: {output_format}

INSTRUCTIONS:
1. Parse and validate prompt list
2. For each prompt in the batch:
   a. Call 'run_ollama_prompt' with:
      - model: "{model}"
      - output_format: "{output_format}"
      - wait_for_result: {not parallel}
3. If parallel=True:
   - Submit all jobs without waiting
   - Use 'list_jobs' to track progress
   - Use 'get_job_status' for each job
4. Collect and format all responses
5. Return organized batch results

TOOLS TO USE:
- run_ollama_prompt: Execute each prompt
- list_jobs: Track all running jobs
- get_job_status: Check individual job status
- run_workflow: Alternative for complex batch operations"""


@mcp.prompt()
async def conversation_flow(
    initial_prompt: str,
    model: str,
    max_turns: Optional[int] = 5,
    context_window: Optional[int] = 4096
) -> str:
    """Manage conversation flow with context retention"""
    return f"""Set up and manage a conversation flow with context retention.

TASK: Create a multi-turn conversation with context management.

INITIAL_PROMPT: {initial_prompt}
MODEL: {model}
MAX_TURNS: {max_turns}
CONTEXT_WINDOW: {context_window}

INSTRUCTIONS:
1. Initialize conversation with 'run_ollama_prompt':
   - Use system_prompt to set context rules
   - Include conversation memory instructions
2. For each conversation turn:
   a. Maintain conversation history
   b. Include relevant context in system_prompt
   c. Call 'run_ollama_prompt' with accumulated context
   d. Track turn count
3. Manage context window:
   - Trim older messages if exceeding {context_window} tokens
   - Preserve important context elements
4. Continue until max_turns reached or conversation concludes

TOOLS TO USE:
- run_ollama_prompt: Execute each conversation turn
- save_script: Save conversation template for reuse
- run_script: Execute saved conversation patterns
- get_job_status: Monitor response generation"""


# Add a comprehensive guide prompt for new users
@mcp.prompt()
async def ollama_guide() -> str:
    """Ollama MCP Server Guide - Interactive guide for using Ollama MCP tools"""
    return """Welcome to the Ollama MCP Server! This interactive guide will help you use the available tools effectively.

QUICK START OPTIONS:
Choose what you want to do:

1. RUN A SIMPLE PROMPT
   Use: ollama_run_prompt
   Example: Run "Explain quantum computing" with model "qwen3:0.6b"

2. COMPARE MODEL RESPONSES
   Use: model_comparison
   Example: Compare how llama3:8b and mistral:7b explain AI

3. CREATE AN AGENT WORKFLOW
   Use: fast_agent_workflow
   Examples:
   - chain: Sequential task processing
   - parallel: Run multiple agents simultaneously
   - evaluator: Iterative content improvement

4. EXECUTE SAVED SCRIPTS
   Use: script_executor
   Example: Run a template with variables

5. ANALYZE MODEL PERFORMANCE
   Use: model_analysis
   Example: Test model capabilities and speed

AVAILABLE TOOLS OVERVIEW:

BASIC OPERATIONS:
- list_ollama_models: See all available models
- run_ollama_prompt: Execute prompts with models
- get_job_status: Check task completion
- list_jobs: View all running/completed jobs

SCRIPT MANAGEMENT:
- save_script: Create reusable prompt templates
- list_scripts: View saved scripts
- get_script: Read script content
- run_script: Execute scripts with variables

WORKFLOW TOOLS:
- create_fastagent_script: Make single-agent scripts
- create_fastagent_workflow: Build multi-agent workflows
- run_fastagent_script: Execute workflows
- list_fastagent_scripts: View available workflows

COMMON WORKFLOW PATTERNS:

1. BASIC PROMPT EXECUTION:
   list_ollama_models → run_ollama_prompt → get_job_status

2. SCRIPT WORKFLOW:
   save_script → list_scripts → run_script → get_job_status

3. AGENT WORKFLOW:
   create_fastagent_workflow → run_fastagent_script → get_job_status

ERROR TROUBLESHOOTING:

- "Model not found": Use list_ollama_models for correct names
- "Script not found": Check exact name with list_scripts
- "Invalid workflow type": Use: chain, parallel, router, evaluator
- "Invalid script type": Use: basic, workflow

TIPS FOR SUCCESS:
1. Always validate model names before use
2. Use descriptive names for scripts and workflows
3. Start with wait_for_result=true for immediate feedback
4. Monitor long tasks with get_job_status
5. Check output files for complete results

Ready to start? Choose an option above or ask for specific help!"""


if __name__ == "__main__":
    mcp.run()
