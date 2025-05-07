#!/usr/bin/env python
"""
Interactive Agent Workflow Environment

A chat-based interface that allows for full interaction with MCP agent workflows.
This application lets you:
1. Configure and launch agent workflows
2. Chat with agents interactively
3. Monitor tool usage and agent operations
4. Save and analyze workflow results
"""

import os
import sys
import time
import json
import asyncio
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from pathlib import Path
import signal
import yaml
import re
from typing import Dict, List, Any, Optional, Tuple, Set


class InteractiveAgentApp:
    def __init__(self, root):
        # Initialize window
        self.root = root
        self.root.title("Interactive Agent Environment")
        self.root.geometry("1200x800")
        
        # App state
        self.active_workflow = None
        self.active_process = None
        self.process_running = False
        self.last_executed_cmd = None
        self.messages = []
        self.config_data = {}
        self.script_source = ""
        
        # Paths
        self.base_dir = Path("/home/ty/Repositories/ai_workspace/ollama-mcp-server")
        self.script_dir = self.base_dir / "fast-agent-scripts"
        self.config_path = self.base_dir / "fastagent.config.yaml"
        
        # Load config
        self.load_config()
        
        # Set up the UI
        self.setup_ui()
        
        # Load available scripts
        self.load_available_scripts()

    def load_config(self):
        """Load the fastagent.config.yaml configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f)
                self.log_info(f"Loaded configuration from {self.config_path}")
            else:
                self.log_error(f"Configuration file not found: {self.config_path}")
        except Exception as e:
            self.log_error(f"Error loading configuration: {e}")
            self.config_data = {}

    def setup_ui(self):
        """Create the main UI components"""
        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for workflow selection and configuration
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Workflow selection
        ttk.Label(self.top_frame, text="Workflow:").pack(side=tk.LEFT, padx=(0, 5))
        self.workflow_var = tk.StringVar()
        self.workflow_combo = ttk.Combobox(self.top_frame, textvariable=self.workflow_var, width=30)
        self.workflow_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.workflow_combo.bind("<<ComboboxSelected>>", self.on_workflow_selected)
        
        # Configure button
        self.config_btn = ttk.Button(self.top_frame, text="⚙️ Configure", command=self.configure_workflow)
        self.config_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # View source button
        self.source_btn = ttk.Button(self.top_frame, text="📄 View Source", command=self.view_source)
        self.source_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.top_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT)
        
        # Main content area - PanedWindow
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left side - Chat area
        self.chat_frame = ttk.LabelFrame(self.paned, text="Agent Chat")
        self.paned.add(self.chat_frame, weight=3)
        
        # Chat messages
        self.chat_text = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            background="#f9f9f9"
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        self.chat_text.tag_configure("user", foreground="#0066CC", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("agent", foreground="#006633", font=("Arial", 10))
        self.chat_text.tag_configure("system", foreground="#666666", font=("Arial", 9, "italic"))
        self.chat_text.tag_configure("error", foreground="#CC0000", font=("Arial", 10, "bold"))
        
        # Input area with buttons
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(
            self.input_frame,
            wrap=tk.WORD,
            height=3,
            font=("Arial", 10)
        )
        self.input_text.pack(fill=tk.X, pady=(0, 5))
        self.input_text.bind("<Control-Return>", self.send_message)
        
        # Helper text
        self.helper_label = ttk.Label(
            self.input_frame, 
            text="Press Ctrl+Enter to send message",
            font=("Arial", 8),
            foreground="#666666"
        )
        self.helper_label.pack(side=tk.LEFT, pady=(0, 5))
        
        # Button frame for input options
        self.button_frame = ttk.Frame(self.input_frame)
        self.button_frame.pack(side=tk.RIGHT, pady=(0, 5))
        
        # Send button
        self.send_btn = ttk.Button(
            self.button_frame,
            text="Send",
            command=self.send_message,
            state=tk.DISABLED
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Start/Stop workflow button
        self.start_btn = ttk.Button(
            self.button_frame,
            text="Start Workflow",
            command=self.toggle_workflow
        )
        self.start_btn.pack(side=tk.LEFT)
        
        # Right side - Details & Monitoring
        self.details_frame = ttk.LabelFrame(self.paned, text="Workflow Details")
        self.paned.add(self.details_frame, weight=2)
        
        # Notebook for details and monitoring
        self.notebook = ttk.Notebook(self.details_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Info tab
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Info")
        
        self.info_text = scrolledtext.ScrolledText(
            self.info_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            background="#f7f7f7"
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Tools tab
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="MCP Tools")
        
        # Available tools
        ttk.Label(self.tools_frame, text="Available MCP Servers:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.tools_text = scrolledtext.ScrolledText(
            self.tools_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            height=10
        )
        self.tools_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        self.logs_text = scrolledtext.ScrolledText(
            self.logs_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            background="#f0f0f0"
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Source tab (hidden until needed)
        self.source_frame = ttk.Frame(self.notebook)
        
        self.source_text = scrolledtext.ScrolledText(
            self.source_frame,
            wrap=tk.NONE,
            font=("Courier", 10),
            background="#f8f8f8"
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add keyboard shortcut for sending
        self.root.bind("<Control-Return>", self.send_message)
        
        # Populate the tools panel with available MCP servers
        self.update_tools_panel()

    def load_available_scripts(self):
        """Load available fast-agent scripts"""
        scripts = []
        try:
            for script_path in sorted(self.script_dir.glob("*.py")):
                # Skip special files
                if script_path.name.startswith("__") or script_path.name.startswith("."):
                    continue
                
                # Check if it's a fast-agent script
                with open(script_path, 'r') as f:
                    content = f.read(2000)
                    if "@fast.agent" in content or "FastAgent" in content:
                        scripts.append(script_path.name)
        except Exception as e:
            self.log_error(f"Error loading scripts: {e}")
        
        # Update the combobox
        self.workflow_combo['values'] = scripts
        if scripts:
            self.workflow_combo.current(0)
            self.on_workflow_selected(None)
            
        self.log_info(f"Found {len(scripts)} fast-agent scripts")

    def on_workflow_selected(self, event):
        """Handle workflow selection"""
        script_name = self.workflow_var.get()
        if not script_name:
            return
            
        script_path = self.script_dir / script_name
        
        # Load the script info
        self.load_script_info(script_path)
        
        # Update the active workflow
        self.active_workflow = script_name
        
        # Clear chat
        self.clear_chat()
        
        # Add welcome message
        self.add_system_message(f"Selected workflow: {script_name}")
        self.add_system_message("Configure and start the workflow to begin interacting with agents.")

    def load_script_info(self, script_path):
        """Load and display script information"""
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                self.script_source = content
            
            # Clear info panel
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            # Extract docstring
            docstring = ""
            if '"""' in content:
                try:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    docstring = content[start:end].strip()
                except:
                    docstring = ""
            
            # Add script info
            self.info_text.insert(tk.END, f"Script: {script_path.name}\n\n")
            
            if docstring:
                self.info_text.insert(tk.END, f"{docstring}\n\n")
            
            # Extract agent and workflow definitions
            agents = self.extract_agents(content)
            workflows = self.extract_workflows(content)
            servers = self.extract_servers(content)
            
            # Add agent info
            if agents:
                self.info_text.insert(tk.END, "Agents:\n")
                for name, details in agents.items():
                    self.info_text.insert(tk.END, f"• {name}\n")
                    if details.get("instruction"):
                        instr = details["instruction"].strip('"\'').replace("\\n", "\n")
                        self.info_text.insert(tk.END, f"  Instruction: {instr[:100]}{'...' if len(instr) > 100 else ''}\n")
                    if details.get("model"):
                        self.info_text.insert(tk.END, f"  Model: {details['model']}\n")
                    if details.get("servers"):
                        servers_str = ", ".join(details["servers"])
                        self.info_text.insert(tk.END, f"  Servers: {servers_str}\n")
                    self.info_text.insert(tk.END, "\n")
            
            # Add workflow info
            if workflows:
                self.info_text.insert(tk.END, "Workflows:\n")
                for name, details in workflows.items():
                    self.info_text.insert(tk.END, f"• {name}\n")
                    if details.get("type"):
                        self.info_text.insert(tk.END, f"  Type: {details['type']}\n")
                    if details.get("sequence"):
                        seq_str = " → ".join(details["sequence"])
                        self.info_text.insert(tk.END, f"  Sequence: {seq_str}\n")
                    self.info_text.insert(tk.END, "\n")
            
            # Add server requirements
            if servers:
                self.info_text.insert(tk.END, "Required MCP Servers:\n")
                available_servers = set(self.get_configured_servers())
                
                for server in servers:
                    status = "✓" if server in available_servers else "✗"
                    color = "green" if server in available_servers else "red"
                    
                    # Create a tag for this server
                    tag_name = f"server_{server}"
                    self.info_text.tag_configure(tag_name, foreground=color)
                    
                    # Insert with tag
                    self.info_text.insert(tk.END, f"• {server} ", tag_name)
                    self.info_text.insert(tk.END, f"({status})\n")
                
                self.info_text.insert(tk.END, "\n")
            
            self.info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_error(f"Error loading script info: {e}")
            import traceback
            traceback.print_exc()

    def extract_agents(self, content):
        """Extract agent definitions from script content"""
        agents = {}
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if "@fast.agent" in line:
                agent_info = {}
                name = self._extract_param(lines, i, 5, "name")
                
                if name:
                    agent_info["name"] = name
                    agent_info["instruction"] = self._extract_param(lines, i, 5, "instruction")
                    agent_info["model"] = self._extract_param(lines, i, 5, "model")
                    
                    # Extract servers
                    servers_str = self._extract_param(lines, i, 5, "servers")
                    if servers_str:
                        # Remove brackets and split
                        servers_str = servers_str.strip("[]")
                        servers = [s.strip().strip('"\'') for s in servers_str.split(",")]
                        agent_info["servers"] = servers
                    
                    agents[name] = agent_info
        
        return agents

    def extract_workflows(self, content):
        """Extract workflow definitions from script content"""
        workflows = {}
        lines = content.split('\n')
        
        workflow_patterns = {
            "@fast.chain": "chain",
            "@fast.router": "router", 
            "@fast.parallel": "parallel",
            "@fast.evaluator_optimizer": "evaluator_optimizer"
        }
        
        for i, line in enumerate(lines):
            for pattern, wf_type in workflow_patterns.items():
                if pattern in line:
                    workflow_info = {"type": wf_type}
                    name = self._extract_param(lines, i, 5, "name")
                    
                    if name:
                        workflow_info["name"] = name
                        
                        # Extract sequence for chain
                        if wf_type == "chain":
                            seq_str = self._extract_param(lines, i, 5, "sequence")
                            if seq_str:
                                seq_str = seq_str.strip("[]")
                                sequence = [s.strip().strip('"\'') for s in seq_str.split(",")]
                                workflow_info["sequence"] = sequence
                        
                        # Extract fan_out for parallel
                        elif wf_type == "parallel":
                            fan_out_str = self._extract_param(lines, i, 5, "fan_out")
                            if fan_out_str:
                                fan_out_str = fan_out_str.strip("[]")
                                fan_out = [s.strip().strip('"\'') for s in fan_out_str.split(",")]
                                workflow_info["sequence"] = fan_out
                        
                        # For evaluator_optimizer
                        elif wf_type == "evaluator_optimizer":
                            generator = self._extract_param(lines, i, 5, "generator")
                            evaluator = self._extract_param(lines, i, 5, "evaluator")
                            if generator and evaluator:
                                workflow_info["sequence"] = [generator, evaluator]
                        
                        # For router
                        elif wf_type == "router":
                            agents_str = self._extract_param(lines, i, 5, "agents")
                            if agents_str:
                                agents_str = agents_str.strip("[]")
                                agents = [s.strip().strip('"\'') for s in agents_str.split(",")]
                                workflow_info["sequence"] = agents
                        
                        workflows[name] = workflow_info
        
        return workflows

    def extract_servers(self, content):
        """Extract all server references from the script"""
        servers = set()
        
        # Look for servers= pattern
        pattern = r'servers\s*=\s*\[(.*?)\]'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            # Extract individual server names
            server_pattern = r"['\"]([^'\"]+)['\"]"
            server_matches = re.findall(server_pattern, match)
            servers.update(server_matches)
        
        return sorted(list(servers))

    def _extract_param(self, lines, start_idx, max_lines, param_name):
        """Extract a parameter from a decorator or function"""
        param_pattern = f"{param_name}="
        
        for i in range(start_idx, min(start_idx + max_lines, len(lines))):
            line = lines[i]
            if param_pattern in line:
                # Find the parameter value
                value_start = line.find(param_pattern) + len(param_pattern)
                value = line[value_start:].strip()
                
                # Handle multi-line values
                if '"""' in value or "'''" in value:
                    # Find the end of the multiline string
                    if '"""' in value:
                        end_marker = '"""'
                    else:
                        end_marker = "'''"
                    
                    # If the end marker is on the same line
                    if value.count(end_marker) >= 2:
                        # Extract between markers
                        start = value.find(end_marker) + len(end_marker)
                        end = value.find(end_marker, start)
                        return value[start:end]
                    else:
                        # Multi-line value
                        result = []
                        # Get the start of the value
                        if end_marker in value:
                            result.append(value.split(end_marker, 1)[1])
                        
                        # Find the end in subsequent lines
                        for j in range(i+1, min(i+10, len(lines))):
                            next_line = lines[j]
                            if end_marker in next_line:
                                result.append(next_line.split(end_marker)[0])
                                break
                            else:
                                result.append(next_line)
                        
                        return "\n".join(result)
                
                # Single line value
                # Remove trailing comma or bracket
                while value and value[-1] in [',', ')', ']']:
                    value = value[:-1]
                
                return value.strip()
        
        return None

    def update_tools_panel(self):
        """Update the tools panel with MCP server information"""
        self.tools_text.config(state=tk.NORMAL)
        self.tools_text.delete(1.0, tk.END)
        
        if not self.config_data or 'mcp' not in self.config_data:
            self.tools_text.insert(tk.END, "No MCP server configuration found.\n")
            self.tools_text.insert(tk.END, f"Please check: {self.config_path}")
            self.tools_text.config(state=tk.DISABLED)
            return
        
        # Get servers from config
        servers = self.config_data.get('mcp', {}).get('servers', {})
        if not servers:
            self.tools_text.insert(tk.END, "No MCP servers configured.\n")
            self.tools_text.config(state=tk.DISABLED)
            return
        
        # Display server information
        self.tools_text.insert(tk.END, f"Found {len(servers)} configured MCP servers:\n\n")
        
        for name, config in servers.items():
            self.tools_text.insert(tk.END, f"Server: {name}\n")
            
            if 'command' in config:
                self.tools_text.insert(tk.END, f"  Command: {config['command']}\n")
            
            if 'args' in config:
                args_str = ' '.join(str(arg) for arg in config['args'])
                self.tools_text.insert(tk.END, f"  Args: {args_str}\n")
            
            if 'env' in config:
                self.tools_text.insert(tk.END, "  Environment Variables:\n")
                for env_name, env_value in config['env'].items():
                    self.tools_text.insert(tk.END, f"    {env_name}={env_value}\n")
            
            self.tools_text.insert(tk.END, "\n")
        
        self.tools_text.config(state=tk.DISABLED)

    def get_configured_servers(self):
        """Get list of configured MCP servers"""
        if not self.config_data or 'mcp' not in self.config_data:
            return []
        
        return list(self.config_data.get('mcp', {}).get('servers', {}).keys())

    def configure_workflow(self):
        """Configure workflow options"""
        # Get the selected workflow
        script_name = self.workflow_var.get()
        if not script_name:
            return
            
        # Read the script content to extract agents and workflows
        script_path = self.script_dir / script_name
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Extract agents and workflows
        agents = self.extract_agents(content)
        workflows = self.extract_workflows(content)
        
        # Create configuration dialog
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title(f"Configure Workflow: {script_name}")
        config_dialog.geometry("500x400")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # Content frame
        content_frame = ttk.Frame(config_dialog, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Target agent/workflow selection
        ttk.Label(content_frame, text="Target Agent or Workflow:").pack(anchor=tk.W, pady=(0, 5))
        
        # Combine agents and workflows for selection
        targets = []
        for name in agents.keys():
            targets.append(f"Agent: {name}")
        for name in workflows.keys():
            targets.append(f"Workflow: {name}")
        
        target_var = tk.StringVar()
        if targets:
            target_var.set(targets[0])
        
        target_combo = ttk.Combobox(content_frame, textvariable=target_var, values=targets, width=40)
        target_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Initial prompt
        ttk.Label(content_frame, text="Initial Prompt/Task:").pack(anchor=tk.W, pady=(0, 5))
        
        prompt_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, height=8)
        prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        prompt_text.insert(tk.END, "What would you like me to help you with?")
        
        # Custom parameters frame
        param_frame = ttk.LabelFrame(content_frame, text="Additional Parameters")
        param_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quiet mode
        quiet_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(param_frame, text="Quiet Mode (less verbose output)", variable=quiet_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        def on_cancel():
            config_dialog.destroy()
        
        def on_start():
            # Extract target name
            target = target_var.get()
            target_name = None
            target_type = None
            
            if target.startswith("Agent:"):
                target_type = "agent"
                target_name = target[7:].strip()
            elif target.startswith("Workflow:"):
                target_type = "workflow"
                target_name = target[10:].strip()
            
            # Get prompt
            initial_prompt = prompt_text.get(1.0, tk.END).strip()
            
            # Close dialog
            config_dialog.destroy()
            
            # Start the workflow
            self.start_workflow(script_name, target_type, target_name, initial_prompt, quiet_var.get())
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Start", command=on_start).pack(side=tk.RIGHT)

    def view_source(self):
        """View the source code of the selected script"""
        script_name = self.workflow_var.get()
        if not script_name:
            return
            
        # If the source tab already exists, just select it
        if self.notebook.tabs()[-1] == str(self.source_frame):
            self.notebook.select(self.source_frame)
            return
            
        # Ensure source is loaded
        if not self.script_source:
            script_path = self.script_dir / script_name
            try:
                with open(script_path, 'r') as f:
                    self.script_source = f.read()
            except Exception as e:
                self.log_error(f"Error reading source: {e}")
                return
        
        # Add the source tab
        self.notebook.add(self.source_frame, text="Source")
        self.notebook.select(self.source_frame)
        
        # Display source
        self.source_text.config(state=tk.NORMAL)
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(tk.END, self.script_source)
        self.source_text.config(state=tk.DISABLED)

    def toggle_workflow(self):
        """Start or stop the current workflow"""
        if self.process_running:
            self.stop_workflow()
        else:
            self.configure_workflow()

    def start_workflow(self, script_name, target_type, target_name, initial_prompt, quiet_mode):
        """Start a workflow with the specified configuration"""
        if self.process_running:
            messagebox.showinfo("Already Running", "A workflow is already running.")
            return
            
        # Build command
        script_path = self.script_dir / script_name
        command = ["uv", "run", str(script_path)]
        
        # Add target if specified
        if target_type and target_name:
            if target_type == "agent":
                command.extend(["--agent", target_name])
            elif target_type == "workflow":
                command.extend(["--agent", target_name])
        
        # Add message if provided
        if initial_prompt:
            command.extend(["--message", initial_prompt])
        
        # Add quiet flag if enabled
        if quiet_mode:
            command.append("--quiet")
        
        # Save the command for debugging
        self.last_executed_cmd = ' '.join(command)
        
        # Update UI
        self.send_btn.config(state=tk.NORMAL)
        self.start_btn.config(text="Stop Workflow")
        self.update_status("Starting workflow...")
        
        # Clear chat
        self.clear_chat()
        
        # Add initial system messages
        self.add_system_message(f"Starting workflow: {script_name}")
        if target_type and target_name:
            self.add_system_message(f"Target: {target_type.capitalize()} '{target_name}'")
        
        if initial_prompt:
            # Add the initial prompt as a user message
            self.add_user_message(initial_prompt)
        
        # Create and start the process
        try:
            # Create process with pipes for I/O
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.base_dir
            )
            
            # Store the process
            self.active_process = process
            self.process_running = True
            
            # Monitor process output
            threading.Thread(
                target=self.monitor_process,
                daemon=True
            ).start()
            
            # Log the command
            self.log_info(f"Executing: {' '.join(command)}")
            
        except Exception as e:
            self.log_error(f"Error starting process: {e}")
            self.update_status(f"Error: {str(e)}")
            self.send_btn.config(state=tk.DISABLED)
            self.start_btn.config(text="Start Workflow")

    def stop_workflow(self):
        """Stop the running workflow"""
        if not self.process_running or not self.active_process:
            return
            
        try:
            # Try to terminate gracefully
            self.active_process.terminate()
            
            # Schedule a check to kill if needed
            self.root.after(2000, self.check_process_termination)
            
            # Update UI
            self.update_status("Stopping workflow...")
            self.add_system_message("Stopping workflow...")
            
        except Exception as e:
            self.log_error(f"Error stopping process: {e}")

    def check_process_termination(self):
        """Check if the process has terminated, kill if still running"""
        if not self.active_process:
            return
            
        if self.active_process.poll() is None:
            # Still running, kill it
            try:
                self.active_process.kill()
                self.add_system_message("Workflow forcefully terminated.")
            except Exception as e:
                self.log_error(f"Error killing process: {e}")
        
        # Reset process state
        self.process_running = False
        self.active_process = None
        
        # Update UI
        self.send_btn.config(state=tk.DISABLED)
        self.start_btn.config(text="Start Workflow")
        self.update_status("Workflow stopped")

    def monitor_process(self):
        """Monitor the output of the running process"""
        if not self.active_process:
            return
            
        collected_output = ""
        agent_response_active = False
        
        # Read output until process terminates
        for line in iter(self.active_process.stdout.readline, ''):
            if line:
                # Log all output
                self.log_info(line.rstrip())
                
                # Filter and process the output for the chat
                if "USER: " in line:
                    # Handle user message echo
                    msg = line.split("USER: ", 1)[1].strip()
                    # Skip adding - already added when sent
                    collected_output = ""
                    agent_response_active = False
                    
                elif "ASSISTANT: " in line:
                    # Start of assistant message
                    msg = line.split("ASSISTANT: ", 1)[1].strip()
                    collected_output = msg
                    agent_response_active = True
                    
                elif agent_response_active:
                    # Continue collecting assistant message
                    collected_output += line
                    
                    # Check if message seems complete
                    if line.strip() == "" and collected_output.strip():
                        # Add the collected message
                        self.add_agent_message(collected_output.strip())
                        collected_output = ""
                        agent_response_active = False
                        
                elif "Error:" in line or "Exception:" in line:
                    # Handle error messages
                    self.add_error_message(line.strip())
                
                # Special case for completion
                if "Workflow completed" in line or "Conversation ended" in line:
                    self.add_system_message("Workflow completed.")
                    # Flush any remaining output
                    if collected_output.strip():
                        self.add_agent_message(collected_output.strip())
                        collected_output = ""
        
        # Process has ended
        # Flush any remaining output
        if collected_output.strip():
            self.add_agent_message(collected_output.strip())
        
        # Update UI after process completion
        self.root.after(0, self.on_process_completed)

    def on_process_completed(self):
        """Handle process completion"""
        if not self.active_process:
            return
            
        # Get return code
        return_code = self.active_process.poll()
        
        # Add completion message
        if return_code == 0:
            self.add_system_message("Workflow completed successfully.")
        else:
            self.add_system_message(f"Workflow exited with code: {return_code}")
        
        # Reset process state
        self.process_running = False
        self.active_process = None
        
        # Update UI
        self.send_btn.config(state=tk.DISABLED)
        self.start_btn.config(text="Start Workflow")
        self.update_status("Workflow finished")

    def send_message(self, event=None):
        """Send a message to the running workflow"""
        if not self.process_running or not self.active_process:
            messagebox.showinfo("Not Running", "No active workflow to send message to.")
            return
            
        # Get the message text
        message = self.input_text.get(1.0, tk.END).strip()
        if not message:
            return
            
        # Clear the input
        self.input_text.delete(1.0, tk.END)
        
        # Add to chat
        self.add_user_message(message)
        
        # Send to process
        try:
            self.active_process.stdin.write(message + "\n")
            self.active_process.stdin.flush()
        except Exception as e:
            self.log_error(f"Error sending message: {e}")
            self.add_error_message(f"Failed to send message: {str(e)}")

    def clear_chat(self):
        """Clear the chat area"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.NORMAL)
        self.messages = []

    def add_user_message(self, text):
        """Add a user message to the chat"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Add newline if not the first message
        if self.messages:
            self.chat_text.insert(tk.END, "\n\n")
        
        # Add message
        self.chat_text.insert(tk.END, "You: ", "user")
        self.chat_text.insert(tk.END, text)
        
        # Scroll to end
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.NORMAL)
        
        # Add to message history
        self.messages.append({"role": "user", "content": text})

    def add_agent_message(self, text):
        """Add an agent message to the chat"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Add newline if not the first message
        if self.messages:
            self.chat_text.insert(tk.END, "\n\n")
        
        # Add message
        self.chat_text.insert(tk.END, "Agent: ", "agent")
        self.chat_text.insert(tk.END, text)
        
        # Scroll to end
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.NORMAL)
        
        # Add to message history
        self.messages.append({"role": "assistant", "content": text})

    def add_system_message(self, text):
        """Add a system message to the chat"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Add newline if not the first message
        if self.messages:
            self.chat_text.insert(tk.END, "\n\n")
        
        # Add message
        self.chat_text.insert(tk.END, f"[System] {text}", "system")
        
        # Scroll to end
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.NORMAL)
        
        # Add to message history
        self.messages.append({"role": "system", "content": text})

    def add_error_message(self, text):
        """Add an error message to the chat"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Add newline if not the first message
        if self.messages:
            self.chat_text.insert(tk.END, "\n\n")
        
        # Add message
        self.chat_text.insert(tk.END, f"[Error] {text}", "error")
        
        # Scroll to end
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.NORMAL)
        
        # Add to message history
        self.messages.append({"role": "system", "content": f"Error: {text}"})

    def log_info(self, message):
        """Log an info message"""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.insert(tk.END, f"{message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state=tk.NORMAL)

    def log_error(self, message):
        """Log an error message"""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.insert(tk.END, f"ERROR: {message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state=tk.NORMAL)

    def update_status(self, message):
        """Update the status label"""
        self.status_var.set(message)


def main():
    # Create the root window
    root = tk.Tk()
    
    # Set application icon if available
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
    except:
        pass
    
    # Create the application
    app = InteractiveAgentApp(root)
    
    # Handle window close
    def on_closing():
        # Stop any running processes
        if app.process_running and app.active_process:
            try:
                app.active_process.terminate()
                time.sleep(0.5)
                if app.active_process.poll() is None:
                    app.active_process.kill()
            except:
                pass
        
        # Close the window
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
