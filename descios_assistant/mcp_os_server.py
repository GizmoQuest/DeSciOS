#!/usr/bin/env python3
"""
MCP OS Context Server for DeSciOS

This server provides OS-aware tools, resources, and prompts for the DeSciOS assistant.
It exposes system monitoring, process management, and desktop environment integration
through the Model Context Protocol (MCP).
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
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("DeSciOS OS Context Server")

class SystemInfo(BaseModel):
    """System information data structure"""
    hostname: str
    platform: str
    architecture: str
    cpu_count: int
    total_memory: int
    available_memory: int
    disk_usage: Dict[str, Any]
    network_interfaces: List[Dict[str, Any]]
    uptime: float
    load_average: List[float]

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

class NetworkInterface(BaseModel):
    """Network interface information"""
    name: str
    addresses: List[str]
    stats: Dict[str, Any]

# Tools for OS operations
@mcp.tool()
def get_system_info() -> SystemInfo:
    """Get comprehensive system information including hardware and resource usage"""
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
                    'percent': (usage.used / usage.total) * 100,
                    'filesystem': partition.device,
                    'fstype': partition.fstype
                }
            except (PermissionError, OSError):
                continue
        
        # Get network interfaces
        network_interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            addresses = []
            for addr in addrs:
                if addr.family == 2:  # IPv4
                    addresses.append(addr.address)
                elif addr.family == 10:  # IPv6
                    addresses.append(addr.address)
            
            if addresses:
                network_interfaces.append({
                    'name': interface,
                    'addresses': addresses
                })
        
        # Get load average (Linux/Unix only)
        try:
            load_avg = list(os.getloadavg())
        except (OSError, AttributeError):
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemInfo(
            hostname=os.uname().nodename,
            platform=os.uname().sysname,
            architecture=os.uname().machine,
            cpu_count=psutil.cpu_count(),
            total_memory=psutil.virtual_memory().total,
            available_memory=psutil.virtual_memory().available,
            disk_usage=disk_usage,
            network_interfaces=network_interfaces,
            uptime=psutil.boot_time(),
            load_average=load_avg
        )
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise

@mcp.tool()
def get_top_processes(limit: int = 10) -> List[ProcessInfo]:
    """Get information about top processes by CPU usage"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 
                                         'memory_percent', 'memory_info', 'status', 
                                         'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None:
                    processes.append(ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        username=pinfo['username'] or 'unknown',
                        cpu_percent=pinfo['cpu_percent'],
                        memory_percent=pinfo['memory_percent'],
                        memory_info=pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                        status=pinfo['status'],
                        create_time=pinfo['create_time'],
                        cmdline=pinfo['cmdline'] or []
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage and return top processes
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        return processes[:limit]
    except Exception as e:
        logger.error(f"Error getting top processes: {e}")
        raise

@mcp.tool()
def get_process_by_name(process_name: str) -> List[ProcessInfo]:
    """Get information about processes by name"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 
                                         'memory_percent', 'memory_info', 'status', 
                                         'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                if pinfo['name'] and process_name.lower() in pinfo['name'].lower():
                    processes.append(ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        username=pinfo['username'] or 'unknown',
                        cpu_percent=pinfo['cpu_percent'] or 0.0,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        memory_info=pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                        status=pinfo['status'],
                        create_time=pinfo['create_time'],
                        cmdline=pinfo['cmdline'] or []
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    except Exception as e:
        logger.error(f"Error getting process by name: {e}")
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
def execute_command(command: str, args: List[str] = None, timeout: int = 30) -> dict:
    """Execute a system command and return output"""
    try:
        cmd_args = [command] + (args or [])
        
        # Security: Only allow specific safe commands
        safe_commands = {
            'ls', 'dir', 'pwd', 'whoami', 'id', 'date', 'uptime',
            'free', 'df', 'ps', 'top', 'htop', 'vmstat', 'iostat',
            'netstat', 'ss', 'ip', 'ifconfig', 'ping', 'nslookup',
            'git', 'python3', 'python', 'pip', 'pip3', 'conda',
            'jupyter', 'jupyter-lab', 'rstudio', 'r', 'octave',
            'spyder', 'code', 'gedit', 'nano', 'vi', 'vim',
            'firefox', 'qgis', 'ugene', 'imagej', 'fiji'
        }
        
        if command not in safe_commands:
            return {
                "success": False,
                "error": f"Command '{command}' not in safe commands list"
            }
        
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": True,
            "command": ' '.join(cmd_args),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_desktop_info() -> dict:
    """Get desktop environment information"""
    try:
        info = {
            "desktop_session": os.environ.get('DESKTOP_SESSION', 'unknown'),
            "display": os.environ.get('DISPLAY', 'unknown'),
            "wayland_display": os.environ.get('WAYLAND_DISPLAY', 'none'),
            "session_type": os.environ.get('XDG_SESSION_TYPE', 'unknown'),
            "current_desktop": os.environ.get('XDG_CURRENT_DESKTOP', 'unknown'),
            "window_manager": os.environ.get('WINDOW_MANAGER', 'unknown')
        }
        
        # Try to get window list using wmctrl
        try:
            result = subprocess.run(['wmctrl', '-l'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                windows = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append({
                                'id': parts[0],
                                'desktop': parts[1],
                                'pid': parts[2],
                                'title': parts[3]
                            })
                info['active_windows'] = windows
        except (subprocess.TimeoutExpired, FileNotFoundError):
            info['active_windows'] = []
        
        return info
    except Exception as e:
        logger.error(f"Error getting desktop info: {e}")
        return {"error": str(e)}

@mcp.tool()
def launch_application(app_name: str, args: List[str] = None) -> dict:
    """Launch a scientific application"""
    try:
        # Mapping of application names to actual commands
        app_commands = {
            'jupyter': ['jupyter', 'lab'],
            'jupyterlab': ['jupyter', 'lab'],
            'rstudio': ['rstudio'],
            'spyder': ['spyder'],
            'octave': ['octave', '--gui'],
            'qgis': ['qgis'],
            'ugene': ['ugene'],
            'fiji': ['fiji'],
            'imagej': ['imagej'],
            'firefox': ['firefox'],
            'thunar': ['thunar'],
            'terminal': ['xfce4-terminal'],
            'calculator': ['qalculate-gtk'],
            'texteditor': ['mousepad']
        }
        
        if app_name.lower() not in app_commands:
            return {
                "success": False,
                "error": f"Application '{app_name}' not supported. Available: {list(app_commands.keys())}"
            }
        
        command = app_commands[app_name.lower()]
        if args:
            command.extend(args)
        
        # Launch application in background
        process = subprocess.Popen(command, 
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
        
        return {
            "success": True,
            "application": app_name,
            "pid": process.pid,
            "command": ' '.join(command)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Resources for OS context
@mcp.resource("os://system/info")
def get_system_resource() -> str:
    """Get system information as a resource"""
    try:
        sys_info = get_system_info()
        return f"""# DeSciOS System Information

## Hardware
- **Hostname**: {sys_info.hostname}
- **Platform**: {sys_info.platform}
- **Architecture**: {sys_info.architecture}
- **CPU Cores**: {sys_info.cpu_count}

## Memory
- **Total**: {sys_info.total_memory / (1024**3):.2f} GB
- **Available**: {sys_info.available_memory / (1024**3):.2f} GB
- **Usage**: {((sys_info.total_memory - sys_info.available_memory) / sys_info.total_memory) * 100:.1f}%

## Load Average
- **1 min**: {sys_info.load_average[0]:.2f}
- **5 min**: {sys_info.load_average[1]:.2f}
- **15 min**: {sys_info.load_average[2]:.2f}

## Network Interfaces
{chr(10).join([f"- **{iface['name']}**: {', '.join(iface['addresses'])}" for iface in sys_info.network_interfaces])}

## Storage
{chr(10).join([f"- **{mount}**: {info['used'] / (1024**3):.1f}GB / {info['total'] / (1024**3):.1f}GB ({info['percent']:.1f}%)" for mount, info in sys_info.disk_usage.items()])}
"""
    except Exception as e:
        return f"Error getting system information: {e}"

@mcp.resource("os://processes/top")
def get_top_processes_resource() -> str:
    """Get top processes as a resource"""
    try:
        processes = get_top_processes(15)
        output = "# Top Processes by CPU Usage\n\n"
        output += "| PID | Name | User | CPU% | Memory% | Status |\n"
        output += "|-----|------|------|------|---------|--------|\n"
        
        for proc in processes:
            output += f"| {proc.pid} | {proc.name} | {proc.username} | {proc.cpu_percent:.1f}% | {proc.memory_percent:.1f}% | {proc.status} |\n"
        
        return output
    except Exception as e:
        return f"Error getting process information: {e}"

@mcp.resource("os://desktop/environment")
def get_desktop_resource() -> str:
    """Get desktop environment information as a resource"""
    try:
        desktop_info = get_desktop_info()
        
        output = "# Desktop Environment Information\n\n"
        output += f"- **Desktop Session**: {desktop_info.get('desktop_session', 'unknown')}\n"
        output += f"- **Display**: {desktop_info.get('display', 'unknown')}\n"
        output += f"- **Session Type**: {desktop_info.get('session_type', 'unknown')}\n"
        output += f"- **Current Desktop**: {desktop_info.get('current_desktop', 'unknown')}\n"
        output += f"- **Window Manager**: {desktop_info.get('window_manager', 'unknown')}\n"
        
        if 'active_windows' in desktop_info and desktop_info['active_windows']:
            output += "\n## Active Windows\n"
            for window in desktop_info['active_windows']:
                output += f"- **{window['title']}** (PID: {window['pid']})\n"
        
        return output
    except Exception as e:
        return f"Error getting desktop information: {e}"

@mcp.resource("os://applications/scientific")
def get_scientific_apps_resource() -> str:
    """Get information about available scientific applications"""
    return """# Available Scientific Applications

## Data Science & Analysis
- **JupyterLab**: Interactive notebook environment for data science
- **RStudio**: Integrated development environment for R
- **Spyder**: Scientific Python IDE
- **GNU Octave**: Mathematical computing environment (MATLAB-like)

## Bioinformatics
- **UGENE**: Bioinformatics suite for sequence analysis
- **CellModeller**: Synthetic biology modeling tool

## Visualization & Imaging
- **Fiji (ImageJ)**: Image processing and analysis
- **QGIS**: Geographic Information System
- **GRASS GIS**: Advanced geospatial analysis
- **NGL Viewer**: Molecular visualization (web-based)

## Development Tools
- **Git**: Version control system
- **Python**: Programming language with scientific libraries
- **R**: Statistical computing language
- **Nextflow**: Workflow management for scientific computing

## Utilities
- **Firefox**: Web browser
- **Thunar**: File manager
- **Terminal**: Command line interface
- **Text Editor**: Code and text editing

Use the `launch_application` tool to start any of these applications.
"""

# Prompts for OS operations
@mcp.prompt()
def system_analysis_prompt(focus_area: str = "general") -> str:
    """Generate a system analysis prompt"""
    return f"""Please analyze the current DeSciOS system focusing on {focus_area}. 

Consider the following aspects:
1. System resource usage (CPU, memory, disk, network)
2. Running processes and their resource consumption
3. Desktop environment and active applications
4. Scientific computing environment status
5. Potential performance issues or optimizations
6. Security considerations

Provide specific recommendations for:
- Resource optimization
- Scientific workflow improvements
- System maintenance tasks
- Performance tuning

Focus particularly on the {focus_area} aspect of the system."""

@mcp.prompt()
def process_troubleshooting_prompt(issue_description: str) -> str:
    """Generate a process troubleshooting prompt"""
    return f"""Help troubleshoot the following process/application issue in DeSciOS:

**Issue**: {issue_description}

Please provide:
1. Diagnostic steps to identify the root cause
2. Commands to check process status and resource usage
3. Potential solutions and workarounds
4. Prevention strategies for similar issues

Consider the scientific computing context of DeSciOS and focus on:
- Impact on running scientific applications
- Data integrity and safety
- Minimal disruption to ongoing research workflows
- Integration with other system components"""

@mcp.prompt()
def application_launcher_prompt(app_category: str = "scientific") -> List[base.Message]:
    """Generate an application launcher prompt"""
    return [
        base.UserMessage(f"I need to launch a {app_category} application in DeSciOS. What are my options?"),
        base.AssistantMessage("""I can help you launch applications in DeSciOS. Here are the available scientific applications:

**Data Science & Analysis:**
- `jupyter` / `jupyterlab` - Interactive notebook environment
- `rstudio` - R integrated development environment  
- `spyder` - Scientific Python IDE
- `octave` - Mathematical computing (MATLAB-like)

**Bioinformatics:**
- `ugene` - Bioinformatics suite
- `cellmodeller` - Synthetic biology modeling

**Visualization:**
- `fiji` - Image processing (ImageJ)
- `qgis` - Geographic Information System
- `imagej` - Image analysis

**Utilities:**
- `firefox` - Web browser
- `thunar` - File manager
- `terminal` - Command line

Which application would you like to launch? I can start it for you using the launch_application tool."""),
        base.UserMessage("Please launch the application I specify and provide any additional setup guidance.")
    ]

def main():
    """Main entry point for the MCP server"""
    try:
        logger.info("Starting DeSciOS OS Context MCP Server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 