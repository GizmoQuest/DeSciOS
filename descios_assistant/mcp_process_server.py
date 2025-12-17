#!/usr/bin/env python3
"""
MCP Process Manager Server for DeSciOS

This server provides process management and monitoring tools for the DeSciOS assistant.
"""

# MIT License
#
# Copyright (c) 2025 Avimanyu Bandyopadhyay
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import json
import logging
import os
import psutil
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("DeSciOS Process Manager Server")

class ProcessInfo(BaseModel):
    """Process information data structure"""
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_info: Dict[str, int]
    status: str
    create_time: float
    cmdline: List[str]
    working_directory: str
    num_threads: int
    connections: List[Dict[str, Any]]

class ProcessTree(BaseModel):
    """Process tree data structure"""
    pid: int
    name: str
    children: List['ProcessTree']
    cpu_percent: float
    memory_percent: float

class SystemResources(BaseModel):
    """System resources data structure"""
    cpu_count: int
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_usage: Dict[str, Any]
    network_io: Dict[str, Any]

@mcp.tool()
def get_all_processes() -> List[ProcessInfo]:
    """Get information about all running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 
                                         'memory_percent', 'memory_info', 'status', 
                                         'create_time', 'cmdline', 'cwd', 'num_threads']):
            try:
                pinfo = proc.info
                processes.append(ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    username=pinfo['username'] or 'unknown',
                    cpu_percent=pinfo['cpu_percent'] or 0.0,
                    memory_percent=pinfo['memory_percent'] or 0.0,
                    memory_info=pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                    status=pinfo['status'],
                    create_time=pinfo['create_time'],
                    cmdline=pinfo['cmdline'] or [],
                    working_directory=pinfo['cwd'] or '',
                    num_threads=pinfo['num_threads'] or 0,
                    connections=[]
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    except Exception as e:
        logger.error(f"Error getting all processes: {e}")
        raise

@mcp.tool()
def get_top_processes(limit: int = 10, sort_by: str = "cpu") -> List[ProcessInfo]:
    """Get top processes by CPU or memory usage"""
    try:
        processes = get_all_processes()
        
        if sort_by.lower() == "memory":
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        else:  # Default to CPU
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        
        return processes[:limit]
    except Exception as e:
        logger.error(f"Error getting top processes: {e}")
        raise

@mcp.tool()
def get_process_by_name(process_name: str) -> List[ProcessInfo]:
    """Get information about processes by name"""
    try:
        processes = get_all_processes()
        return [p for p in processes if process_name.lower() in p.name.lower()]
    except Exception as e:
        logger.error(f"Error getting process by name: {e}")
        raise

@mcp.tool()
def get_process_by_pid(pid: int) -> ProcessInfo:
    """Get information about a specific process by PID"""
    try:
        proc = psutil.Process(pid)
        pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 
                                   'memory_percent', 'memory_info', 'status', 
                                   'create_time', 'cmdline', 'cwd', 'num_threads'])
        
        return ProcessInfo(
            pid=pinfo['pid'],
            name=pinfo['name'],
            username=pinfo['username'] or 'unknown',
            cpu_percent=pinfo['cpu_percent'] or 0.0,
            memory_percent=pinfo['memory_percent'] or 0.0,
            memory_info=pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
            status=pinfo['status'],
            create_time=pinfo['create_time'],
            cmdline=pinfo['cmdline'] or [],
            working_directory=pinfo['cwd'] or '',
            num_threads=pinfo['num_threads'] or 0,
            connections=[]
        )
    except psutil.NoSuchProcess:
        raise ValueError(f"Process with PID {pid} not found")
    except Exception as e:
        logger.error(f"Error getting process by PID: {e}")
        raise

@mcp.tool()
def kill_process(pid: int, signal: int = 15) -> dict:
    """Kill a process by PID (signal 15=SIGTERM, 9=SIGKILL)"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        
        # Send signal to process
        process.send_signal(signal)
        
        # Wait a bit to see if process terminates
        try:
            process.wait(timeout=3)
            status = "terminated"
        except psutil.TimeoutExpired:
            status = "signal_sent"
        
        return {
            "success": True,
            "pid": pid,
            "process_name": process_name,
            "signal": signal,
            "status": status
        }
    except psutil.NoSuchProcess:
        return {
            "success": False,
            "error": f"Process with PID {pid} not found"
        }
    except psutil.AccessDenied:
        return {
            "success": False,
            "error": f"Access denied to kill process {pid}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def start_process(command: str, args: List[str] = None, background: bool = True) -> dict:
    """Start a new process"""
    try:
        cmd_args = [command] + (args or [])
        
        # Security: Only allow specific safe commands
        safe_commands = {
            'jupyter', 'jupyter-lab', 'rstudio', 'spyder', 'octave',
            'qgis', 'ugene', 'fiji', 'firefox', 'thunar', 'xfce4-terminal',
            'python3', 'python', 'r', 'git', 'ls', 'pwd', 'whoami'
        }
        
        if command not in safe_commands:
            return {
                "success": False,
                "error": f"Command '{command}' not in safe commands list"
            }
        
        if background:
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        else:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "pid": None,
                "command": ' '.join(cmd_args),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        return {
            "success": True,
            "pid": process.pid,
            "command": ' '.join(cmd_args),
            "background": background
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_process_tree(pid: int = None) -> ProcessTree:
    """Get process tree starting from a specific PID or root"""
    try:
        if pid is None:
            # Get root process (usually PID 1)
            root_proc = psutil.Process(1)
        else:
            root_proc = psutil.Process(pid)
        
        def build_tree(proc):
            try:
                children = []
                for child in proc.children():
                    try:
                        children.append(build_tree(child))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                return ProcessTree(
                    pid=proc.pid,
                    name=proc.name(),
                    children=children,
                    cpu_percent=proc.cpu_percent() or 0.0,
                    memory_percent=proc.memory_percent() or 0.0
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return ProcessTree(
                    pid=proc.pid,
                    name="unknown",
                    children=[],
                    cpu_percent=0.0,
                    memory_percent=0.0
                )
        
        return build_tree(root_proc)
    except Exception as e:
        logger.error(f"Error getting process tree: {e}")
        raise

@mcp.tool()
def get_system_resources() -> SystemResources:
    """Get current system resource usage"""
    try:
        # Get disk usage for all mounted filesystems
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                }
            except (PermissionError, OSError):
                continue
        
        # Get network I/O
        network_io = {}
        try:
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            network_io = {}
        
        return SystemResources(
            cpu_count=psutil.cpu_count(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_total=psutil.virtual_memory().total,
            memory_available=psutil.virtual_memory().available,
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=disk_usage,
            network_io=network_io
        )
    except Exception as e:
        logger.error(f"Error getting system resources: {e}")
        raise

@mcp.resource("process://all/running")
def get_all_processes_resource() -> str:
    """Get all running processes as a resource"""
    try:
        processes = get_top_processes(20, "cpu")
        
        output = "# Running Processes (Top 20 by CPU)\n\n"
        output += "| PID | Name | User | CPU% | Memory% | Status |\n"
        output += "|-----|------|------|------|---------|--------|\n"
        
        for proc in processes:
            output += f"| {proc.pid} | {proc.name} | {proc.username} | {proc.cpu_percent:.1f}% | {proc.memory_percent:.1f}% | {proc.status} |\n"
        
        return output
    except Exception as e:
        return f"Error getting process information: {e}"

@mcp.resource("process://system/resources")
def get_system_resources_resource() -> str:
    """Get system resources as a resource"""
    try:
        resources = get_system_resources()
        
        output = "# System Resources\n\n"
        output += f"## CPU\n"
        output += f"- **Cores**: {resources.cpu_count}\n"
        output += f"- **Usage**: {resources.cpu_percent:.1f}%\n\n"
        
        output += f"## Memory\n"
        output += f"- **Total**: {resources.memory_total / (1024**3):.2f} GB\n"
        output += f"- **Available**: {resources.memory_available / (1024**3):.2f} GB\n"
        output += f"- **Usage**: {resources.memory_percent:.1f}%\n\n"
        
        output += f"## Storage\n"
        for mount, info in resources.disk_usage.items():
            output += f"- **{mount}**: {info['used'] / (1024**3):.1f}GB / {info['total'] / (1024**3):.1f}GB ({info['percent']:.1f}%)\n"
        
        if resources.network_io:
            output += f"\n## Network I/O\n"
            output += f"- **Bytes Sent**: {resources.network_io['bytes_sent'] / (1024**2):.2f} MB\n"
            output += f"- **Bytes Received**: {resources.network_io['bytes_recv'] / (1024**2):.2f} MB\n"
        
        return output
    except Exception as e:
        return f"Error getting system resources: {e}"

def main():
    """Main entry point"""
    logger.info("Starting DeSciOS Process Manager MCP Server...")
    mcp.run()

if __name__ == "__main__":
    main() 