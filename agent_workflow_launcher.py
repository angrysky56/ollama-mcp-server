#!/usr/bin/env python
"""
MCP Agent Workflow Launcher

A practical GUI for executing fast-agent scripts with MCP servers.
This tool allows you to easily run, monitor, and interact with agent workflows.
"""

import os
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import pty
import fcntl
import termios
import struct
import select
import re


class WorkflowLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Agent Workflow Launcher")
        self.root.geometry("900x700")

        # Configure styles
        self.configure_styles()

        # Initialize state variables
        self.processes = {}
        self.input_queue = []
        self.script_dir = Path("/home/ty/Repositories/ai_workspace/ollama-mcp-server/fast-agent-scripts")
        self.ollama_models = []

        # Create main layout
        self.create_layout()

        # Populate script list and model list
        self.refresh_scripts()
        self.refresh_models()

        # Set up periodic checks for process status
        self.root.after(1000, self.check_processes)

    def configure_styles(self):
        """Set up custom styles for the UI"""
        style = ttk.Style()

        # Try to use a modern theme if available
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Configure button styles
        style.configure("Run.TButton",
                        background="#4CAF50",
                        foreground="black",
                        padding=5)
        style.configure("Stop.TButton",
                        background="#F44336",
                        foreground="black",
                        padding=5)

        # Configure headings
        style.configure("TLabelframe.Label",
                       font=("Helvetica", 11, "bold"))
    def create_layout(self):
        """Create the main application layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top panel - script selection and controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Script list panel (left side)
        script_frame = ttk.LabelFrame(top_frame, text="Available Workflows")
        script_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Scrollable script list
        script_list_frame = ttk.Frame(script_frame)
        script_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        y_scrollbar = ttk.Scrollbar(script_list_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.script_listbox = tk.Listbox(
            script_list_frame,
            font=("Courier", 10),
            selectbackground="#5c5c5c",
            selectforeground="white",
            activestyle="none"
        )
        self.script_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.script_listbox.config(yscrollcommand=y_scrollbar.set)
        y_scrollbar.config(command=self.script_listbox.yview)

        # Bind selection event
        self.script_listbox.bind("<<ListboxSelect>>", self.on_script_select)

        # Script details panel (right side)
        details_frame = ttk.LabelFrame(top_frame, text="Workflow Details")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            height=10,
            font=("Courier", 10),
            background="#f8f8f8"
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Model selector frame
        model_frame = ttk.Frame(control_frame)
        model_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(model_frame, text="Ollama Model:").pack(side=tk.LEFT, padx=(0, 5))

        # Model selector dropdown
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            width=20,
            state="readonly"
        )
        self.model_combobox.pack(side=tk.LEFT)

        # Refresh models button
        ttk.Button(
            model_frame,
            text="🔄",
            width=2,
            command=self.refresh_models
        ).pack(side=tk.LEFT, padx=2)

        # Refresh button
        self.refresh_btn = ttk.Button(
            control_frame,
            text="🔄 Refresh Scripts",
            command=self.refresh_scripts
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(10, 5))

        # Run button
        self.run_btn = ttk.Button(
            control_frame,
            text="▶️ Run Workflow",
            style="Run.TButton",
            command=self.run_selected_script
        )
        self.run_btn.pack(side=tk.LEFT, padx=5)
        self.run_btn.config(state=tk.DISABLED)

        # Stop button
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹️ Stop Workflow",
            style="Stop.TButton",
            command=self.stop_selected_script
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state=tk.DISABLED)

        # Clear output button
        self.clear_btn = ttk.Button(
            control_frame,
            text="🧹 Clear Output",
            command=self.clear_output
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            control_frame,
            textvariable=self.status_var,
            font=("Helvetica", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Output panel
        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill=tk.BOTH, expand=True)

        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Courier", 10),
            background="#f0f0f0"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Input frame for sending commands to running scripts
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        # Input entry
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Courier", 10)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Send button
        self.send_btn = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_input
        )
        self.send_btn.pack(side=tk.RIGHT)
        self.send_btn.config(state=tk.DISABLED)

        # Enter key binding with focus handling
        self.input_entry.bind("<Return>", lambda e: self.send_input())
        self.input_entry.bind("<KeyRelease>", self.check_input_key)

        # Give focus to input field whenever it's enabled
        self.input_entry.bind("<FocusIn>", lambda e: self.root.after(100, self.ensure_input_focus))

    def refresh_models(self):
        """Refresh the list of available Ollama models"""
        # Save current selection if any
        current_selection = self.model_var.get()

        # Clear the combobox
        self.model_combobox['values'] = []
        self.ollama_models = []

        # Update status
        self.update_status("Fetching Ollama models...")

        try:
            # Run ollama list command to get available models
            process = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the output
            lines = process.stdout.strip().split('\n')

            # Process each line (skip header)
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if parts and len(parts) >= 1:
                        model_name = parts[0]
                        self.ollama_models.append(model_name)

            # Sort models alphabetically
            self.ollama_models.sort()

            # Update combobox
            if self.ollama_models:
                self.model_combobox['values'] = self.ollama_models

                # Restore previous selection or select first model
                if current_selection in self.ollama_models:
                    self.model_var.set(current_selection)
                else:
                    self.model_var.set(self.ollama_models[0])

                # Update status
                self.update_status(f"Found {len(self.ollama_models)} Ollama models")
            else:
                self.update_status("No Ollama models found", error=True)

        except Exception as e:
            self.update_status(f"Error fetching Ollama models: {e}", error=True)

            # Add a default option if we can't get real models
            self.model_combobox['values'] = ["llama3:latest"]
            self.model_var.set("llama3:latest")

    def refresh_scripts(self):
        """Refresh the list of available scripts"""
        self.script_listbox.delete(0, tk.END)

        # Get all Python files in the script directory
        scripts = sorted(self.script_dir.glob("*.py"))

        # Filter out files that don't look like fast-agent scripts
        agent_scripts = []
        for script in scripts:
            # Skip __init__.py and other special files
            if script.name.startswith("__") or script.name.startswith("."):
                continue

            # Read a bit of the file to check if it looks like a fast-agent script
            try:
                with open(script, 'r') as f:
                    content = f.read(2000)  # Read the first part of the file
                    if "@fast.agent" in content or "FastAgent" in content:
                        agent_scripts.append(script)
            except Exception:
                # Skip files that can't be read
                continue

        # Add scripts to the listbox
        for script in agent_scripts:
            self.script_listbox.insert(tk.END, script.name)

        # Update status
        self.update_status(f"Found {len(agent_scripts)} fast-agent scripts")

    def on_script_select(self, event):
        """Handle script selection from the listbox"""
        if not self.script_listbox.curselection():
            return

        # Get the selected script name
        index = self.script_listbox.curselection()[0]
        script_name = self.script_listbox.get(index)

        # Enable the run button
        self.run_btn.config(state=tk.NORMAL)

        # Check if this script is running
        if script_name in self.processes and self.processes[script_name]["process"].poll() is None:
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.stop_btn.config(state=tk.DISABLED)

        # Show script details
        self.show_script_details(script_name)

    def show_script_details(self, script_name):
        """Display details about the selected script"""
        script_path = self.script_dir / script_name

        try:
            # Read the script content
            with open(script_path, 'r') as f:
                content = f.read()

            # Clear details text
            self.details_text.delete(1.0, tk.END)

            # Extract docstring
            docstring = ""
            if '"""' in content:
                try:
                    start = content.index('"""') + 3
                    end = content.index('"""', start)
                    docstring = content[start:end].strip()
                except ValueError:
                    # Malformed docstring
                    pass

            # Display script info
            self.details_text.insert(tk.END, f"Script: {script_name}\n\n")

            if docstring:
                self.details_text.insert(tk.END, f"{docstring}\n\n")

            # Extract agent and workflow definitions
            agents = []
            workflows = []

            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "@fast.agent" in line:
                    # Look for name parameter
                    name = self.extract_parameter(lines, i, "name")
                    if name:
                        agents.append(name)

                elif any(wf in line for wf in ["@fast.chain", "@fast.router", "@fast.parallel", "@fast.evaluator_optimizer"]):
                    # Look for name parameter
                    name = self.extract_parameter(lines, i, "name")
                    if name:
                        workflows.append(name)

            # Display agents
            if agents:
                self.details_text.insert(tk.END, "Agents:\n")
                for agent in agents:
                    self.details_text.insert(tk.END, f"  • {agent}\n")
                self.details_text.insert(tk.END, "\n")

            # Display workflows
            if workflows:
                self.details_text.insert(tk.END, "Workflows:\n")
                for workflow in workflows:
                    self.details_text.insert(tk.END, f"  • {workflow}\n")
                self.details_text.insert(tk.END, "\n")

            # Show MCP servers used
            servers = self.extract_servers(content)
            if servers:
                self.details_text.insert(tk.END, "MCP Servers:\n")
                for server in servers:
                    self.details_text.insert(tk.END, f"  • {server}\n")

        except Exception as e:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error reading script: {e}")

    def extract_parameter(self, lines, start_index, param_name):
        """Extract a parameter value from decorator or function definition"""
        # Look in the next few lines for the parameter
        for i in range(start_index, min(start_index + 5, len(lines))):
            line = lines[i]
            param_pattern = f"{param_name}="
            if param_pattern in line:
                # Extract the value
                value_start = line.index(param_pattern) + len(param_pattern)
                value = line[value_start:].strip()

                # Remove trailing comma or parenthesis
                while value and value[-1] in [',', ')', ']']:
                    value = value[:-1]

                # Remove quotes
                value = value.strip('"\'')

                return value

        return None

    def extract_servers(self, content):
        """Extract MCP servers used in the script"""
        servers = set()

        # Look for servers parameter in agent definitions
        pattern = "servers=["
        if pattern in content:
            # Find all occurrences
            start = 0
            while True:
                start = content.find(pattern, start)
                if start == -1:
                    break

                # Extract the server list
                bracket_start = content.find("[", start)
                bracket_end = content.find("]", bracket_start)

                if bracket_start != -1 and bracket_end != -1:
                    server_list = content[bracket_start+1:bracket_end]

                    # Parse server names
                    for server in server_list.split(","):
                        server = server.strip().strip('"\'')
                        if server:
                            servers.add(server)

                start = bracket_end

        return sorted(list(servers))

    def run_selected_script(self):
        """Run the selected script"""
        if not self.script_listbox.curselection():
            return

        # Get the selected script name
        index = self.script_listbox.curselection()[0]
        script_name = self.script_listbox.get(index)

        # Check if already running
        if script_name in self.processes and self.processes[script_name]["process"].poll() is None:
            messagebox.showinfo("Already Running", f"The script '{script_name}' is already running.")
            return

        # Get selected model
        selected_model = self.model_var.get()
        if not selected_model and self.ollama_models:
            selected_model = self.ollama_models[0]
            self.model_var.set(selected_model)

        # Format model for fast-agent compatibility - need to prefix with 'generic.' for Ollama models
        formatted_model = f"generic.{selected_model}"

        # Build command
        script_path = self.script_dir / script_name
        command = ["uv", "run", str(script_path), "--model", formatted_model]

        # Update UI
        self.update_status(f"Starting: {script_name}")
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)

        # Give focus to the input entry for immediate interaction
        self.input_entry.focus_set()

        # Add header to output
        self.clear_output()
        self.append_output(f"{'='*40}\n")
        self.append_output(f"RUNNING: {script_name}\n")
        self.append_output(f"MODEL: {selected_model}\n")
        self.append_output(f"COMMAND: {' '.join(command)}\n")
        self.append_output(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.append_output(f"{'='*40}\n\n")

        # Create and start the process
        try:
            # Set environment variables
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            # Ensure TERM is set to support color output
            env['TERM'] = 'xterm-256color'

            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()

            # Set terminal size to a suitable dimension
            try:
                # Get the size of the output text area to set proper dimensions
                width = self.output_text.winfo_width() // 8  # Approximate character width
                height = self.output_text.winfo_height() // 16  # Approximate character height

                # Ensure reasonable minimum size
                width = max(width, 80)
                height = max(height, 24)

                # Set the terminal size
                term_size = struct.pack("HHHH", height, width, 0, 0)
                fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, term_size)
            except Exception as e:
                # If setting window size fails, use sensible defaults
                term_size = struct.pack("HHHH", 24, 80, 0, 0)
                fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, term_size)
                self.append_output(f"[NOTE: Using default terminal size (80x24): {e}]\n")

            # Create process with PTY
            process = subprocess.Popen(
                command,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                text=False,  # Binary mode for PTY
                preexec_fn=os.setsid,  # Create a new process group
                cwd=self.script_dir.parent,  # Run from parent directory
                env=env
            )

            # Close the slave end of the PTY in the parent process
            os.close(slave_fd)

            # Set non-blocking mode on the master file descriptor
            old_flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

            # Store process info
            self.processes[script_name] = {
                "process": process,
                "start_time": time.time(),
                "alive": True,
                "master_fd": master_fd
            }

            # Create thread to read output from the PTY
            output_thread = threading.Thread(
                target=self.monitor_pty_output,
                args=(master_fd, script_name),
                daemon=True
            )
            output_thread.start()

        except Exception as e:
            self.append_output(f"Error launching process: {e}\n")
            self.update_status(f"Error: {e}", error=True)
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)

    def monitor_pty_output(self, master_fd, script_name):
        """Thread function to monitor output from a PTY master file descriptor"""
        buffer = b""
        read_buffer_size = 1024

        try:
            # Continue reading until process terminates or fd is closed
            while True:
                # Check if process info still exists and process is alive
                if script_name not in self.processes or not self.processes[script_name]["alive"]:
                    break

                # Check if process has terminated
                if self.processes[script_name]["process"].poll() is not None:
                    break

                # Wait for data with timeout
                try:
                    r, w, e = select.select([master_fd], [], [], 0.1)
                    if master_fd in r:
                        # Read available data
                        try:
                            data = os.read(master_fd, read_buffer_size)
                            if not data:  # EOF
                                break

                            # Process received data
                            buffer += data

                            # Process complete lines (and handle terminal control sequences)
                            lines = []
                            while b'\r' in buffer or b'\n' in buffer:
                                # Find line endings
                                cr_pos = buffer.find(b'\r')
                                lf_pos = buffer.find(b'\n')

                                # Handle different line endings
                                if cr_pos >= 0 and (lf_pos < 0 or cr_pos < lf_pos):
                                    # CR only or CR before LF
                                    line = buffer[:cr_pos]
                                    buffer = buffer[cr_pos + 1:]
                                    lines.append(line)
                                elif lf_pos >= 0:
                                    # LF
                                    line = buffer[:lf_pos]
                                    buffer = buffer[lf_pos + 1:]
                                    lines.append(line)
                                else:
                                    break

                            # Process and display lines
                            for line in lines:
                                try:
                                    # Try to decode as UTF-8
                                    decoded_line = line.decode('utf-8')

                                    # Clean ANSI escape sequences for display
                                    # Simple cleaning for basic ANSI codes
                                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                    cleaned_line = ansi_escape.sub('', decoded_line)

                                    # Add to output display
                                    if cleaned_line:
                                        self.root.after(0, lambda line=cleaned_line: self.append_output(line + '\n'))
                                except UnicodeDecodeError:
                                    # Handle binary data that can't be decoded
                                    pass

                            # If any data remains in buffer, display it if it's substantial
                            if len(buffer) > 0 and not any(c in buffer for c in [b'\r', b'\n', b'\x1b']):
                                try:
                                    remaining = buffer.decode('utf-8')
                                    if remaining and len(remaining) > 0:
                                        self.root.after(0, lambda r=remaining: self.append_output(r))
                                        buffer = b""
                                except UnicodeDecodeError:
                                    # Keep binary data in buffer until we get more complete UTF-8 sequences
                                    pass
                        except OSError as e:
                            # Handle read errors (e.g., fd closed)
                            if e.errno in (5, 9):  # Input/output error or Bad file descriptor
                                break
                            raise
                except Exception as e:
                    # Unexpected error in select - log and continue
                    self.root.after(0, lambda e=e: self.append_output(f"[PTY read error: {e}]\n"))
                    time.sleep(0.1)  # Prevent tight loop on error

                # Small sleep to prevent CPU hogging
                time.sleep(0.01)

            # Process has finished - signal UI update on main thread
            self.root.after(0, lambda: self.process_finished(script_name))

        except Exception as e:
            # Log any unexpected errors
            self.root.after(0, lambda e=e: self.append_output(f"[Error monitoring PTY: {e}]\n"))
            self.root.after(0, lambda: self.process_finished(script_name))
        finally:
            # Ensure the master fd is closed
            try:
                os.close(master_fd)
            except OSError:
                pass
    def process_finished(self, script_name):
        """Handle process completion"""
        if script_name not in self.processes:
            return

        process_info = self.processes[script_name]
        process = process_info["process"]

        # Get return code
        return_code = process.poll()

        # Calculate duration
        duration = time.time() - process_info["start_time"]

        # Add footer to output
        self.append_output(f"\n{'='*40}\n")
        self.append_output(f"FINISHED: {script_name}\n")
        self.append_output(f"RETURN CODE: {return_code}\n")
        self.append_output(f"DURATION: {duration:.2f} seconds\n")
        self.append_output(f"{'='*40}\n\n")

        # Update state
        process_info["alive"] = False

        # Update UI
        self.update_status(f"Completed: {script_name}")
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.input_entry.config(state=tk.DISABLED)

    def stop_selected_script(self):
        """Stop the currently running script"""
        if not self.script_listbox.curselection():
            return

        # Get the selected script name
        index = self.script_listbox.curselection()[0]
        script_name = self.script_listbox.get(index)

        # Check if running
        if script_name not in self.processes or not self.processes[script_name]["alive"]:
            messagebox.showinfo("Not Running", f"The script '{script_name}' is not running.")
            return

        # Confirm action
        if not messagebox.askyesno("Confirm Stop", f"Are you sure you want to stop '{script_name}'?"):
            return

        # Get process
        process = self.processes[script_name]["process"]

        # Try to terminate gracefully
        try:
            self.append_output("\n[STOPPING PROCESS...]\n")

            # Send SIGTERM
            process.terminate()

            # Schedule a check to kill if needed
            self.root.after(2000, lambda: self.force_kill_if_needed(script_name))

        except Exception as e:
            self.append_output(f"Error stopping process: {e}\n")

    def force_kill_if_needed(self, script_name):
        """Kill the process forcefully if it's still running"""
        if script_name not in self.processes:
            return

        process_info = self.processes[script_name]
        process = process_info["process"]

        # Check if still running
        if process.poll() is None:
            try:
                # Send SIGKILL
                process.kill()
                self.append_output("[PROCESS FORCEFULLY KILLED]\n")
            except Exception as e:
                self.append_output(f"Error killing process: {e}\n")

        # Update state
        process_info["alive"] = False

        # Update UI
        self.update_status(f"Stopped: {script_name}")
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

    def send_input(self):
        """Send input to the running process via PTY"""
        # Get input text
        input_text = self.input_var.get()
        if not input_text:
            return

        # Clear input field
        self.input_var.set("")

        # Get selected script
        if not self.script_listbox.curselection():
            return

        index = self.script_listbox.curselection()[0]
        script_name = self.script_listbox.get(index)

        # Check if script is running
        if script_name not in self.processes or not self.processes[script_name]["alive"]:
            messagebox.showinfo("Not Running", "No running process to send input to.")
            return

        # Get master file descriptor from process info
        if "master_fd" not in self.processes[script_name]:
            self.append_output("[ERROR: TTY connection not available]\n")
            return

        master_fd = self.processes[script_name]["master_fd"]

        # Echo input to output with agent name for clarity
        self.append_output(f"[USER]> {input_text}\n")

        # Send input to process with proper newline
        try:
            # Ensure input ends with newline
            if not input_text.endswith('\n'):
                input_text += '\n'

            # Convert to bytes and write to the PTY
            encoded_input = input_text.encode('utf-8')
            os.write(master_fd, encoded_input)

            # Immediately give focus back to input field
            self.ensure_input_focus()
        except Exception as e:
            self.append_output(f"[ERROR: Failed to send input: {e}]\n")

    def check_processes(self):
        """Periodically check the status of running processes"""
        for script_name, process_info in list(self.processes.items()):
            if process_info["alive"] and process_info["process"].poll() is not None:
                # Process has terminated unexpectedly
                self.process_finished(script_name)

        # Re-schedule check
        self.root.after(1000, self.check_processes)

    def append_output(self, text):
        """Add text to the output area"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear the output area"""
        self.output_text.delete(1.0, tk.END)

    def update_status(self, message, error=False):
        """Update the status message"""
        self.status_var.set(message)
        if error:
            self.status_label.config(foreground="red")
        else:
            self.status_label.config(foreground="green")

    def check_input_key(self, event):
        """Handle key events in the input field"""
        # Give focus to input field if it's enabled
        # This ensures that when typing, focus stays in the input field
        if self.input_entry['state'] != 'disabled':
            self.input_entry.focus_set()

    def ensure_input_focus(self):
        """Ensure the input field has focus"""
        if self.input_entry['state'] != 'disabled':
            self.input_entry.focus_set()


def main():
    # Create the main window
    root = tk.Tk()

    # Create and run the application
    app = WorkflowLauncher(root)

    # Handle window close
    def on_closing():
        # Stop all running processes
        for script_name, process_info in list(app.processes.items()):
            if process_info["alive"]:
                try:
                    process_info["process"].terminate()
                except Exception:
                    pass

        # Close window
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
