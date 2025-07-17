#!/usr/bin/env python3
"""
MCP Client for DeSciOS Assistant

This module provides MCP (Model Context Protocol) client capabilities
for OS-aware context management, real-time system monitoring, and
integration with OS-level resources and tools.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import (
    Resource, Tool, Prompt, TextContent, 
    CallToolResult, ResourceTemplate
)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = None
    description: str = ""
    enabled: bool = True

class OSContextData(BaseModel):
    """OS context data structure"""
    processes: List[Dict[str, Any]] = Field(default_factory=list)
    memory_usage: Dict[str, Any] = Field(default_factory=dict)
    cpu_usage: float = 0.0
    disk_usage: Dict[str, Any] = Field(default_factory=dict)
    network_info: Dict[str, Any] = Field(default_factory=dict)
    active_windows: List[Dict[str, Any]] = Field(default_factory=list)
    running_applications: List[str] = Field(default_factory=list)
    last_updated: str = ""

class MCPClientManager:
    """Manager for MCP client connections and OS context"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.os_context: OSContextData = OSContextData()
        self.running = False
        self.context_update_interval = 2.0  # seconds
        self._setup_default_servers()
        # Enable debug logging for memory issues
        logging.basicConfig(level=logging.DEBUG)
    
    def _setup_default_servers(self):
        """Setup default OS-aware MCP servers"""
        # Try multiple possible paths for the server files
        possible_paths = [
            os.path.dirname(__file__),  # Current directory
            "/opt/descios_assistant",   # Container path
            "/home/avi/DeSciOS/descios_assistant"  # Host path
        ]
        
        def find_server_file(filename):
            for path in possible_paths:
                full_path = os.path.join(path, filename)
                if os.path.exists(full_path):
                    return full_path
            return None
        
        self.servers = {}
        
        # OS Context Server
        os_server_path = find_server_file("mcp_os_server.py")
        if os_server_path:
            self.servers["os_context"] = MCPServerConfig(
                name="OS Context Server",
                command="python3",
                args=[os_server_path],
                description="Provides real-time OS context and system monitoring",
                env={"PYTHONPATH": os.path.dirname(os_server_path)}
            )
        
        # Filesystem Server
        fs_server_path = find_server_file("mcp_filesystem_server.py")
        if fs_server_path:
            self.servers["filesystem"] = MCPServerConfig(
                name="Filesystem Server", 
                command="python3",
                args=[fs_server_path],
                description="Provides filesystem operations and file context",
                env={"PYTHONPATH": os.path.dirname(fs_server_path)}
            )
        
        # Process Manager Server
        proc_server_path = find_server_file("mcp_process_server.py")
        if proc_server_path:
            self.servers["process_manager"] = MCPServerConfig(
                name="Process Manager Server",
                command="python3", 
                args=[proc_server_path],
                description="Provides process management and monitoring tools",
                env={"PYTHONPATH": os.path.dirname(proc_server_path)}
            )
        
        logger.info(f"Found {len(self.servers)} MCP servers: {list(self.servers.keys())}")
    
    async def start(self):
        """Start the MCP client manager"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting MCP Client Manager...")
        
        # Start connections to enabled servers
        for server_id, config in self.servers.items():
            if config.enabled:
                try:
                    await self._connect_to_server(server_id, config)
                except Exception as e:
                    logger.error(f"Failed to connect to server {server_id}: {e}")
        
        # Start context update loop
        asyncio.create_task(self._context_update_loop())
    
    async def stop(self):
        """Stop the MCP client manager"""
        self.running = False
        
        # Close all sessions
        for session in self.sessions.values():
            try:
                await session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
        
        self.sessions.clear()
        logger.info("MCP Client Manager stopped")
    
    async def _connect_to_server(self, server_id: str, config: MCPServerConfig):
        """Connect to an MCP server"""
        try:
            # Check if the server file exists
            if config.args and len(config.args) > 0:
                server_file = config.args[0]
                if not os.path.exists(server_file):
                    logger.warning(f"MCP server file not found: {server_file}")
                    return
            
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env or {}
            )
            
            # For now, we'll just log the connection attempt
            # In a full implementation, you'd establish and maintain the connection
            logger.info(f"Would connect to MCP server: {config.name}")
            logger.info(f"Command: {config.command} {' '.join(config.args)}")
            
        except Exception as e:
            logger.error(f"Failed to connect to server {server_id}: {e}")
            # Don't raise the exception, just log it and continue
            logger.warning(f"Continuing without MCP server {server_id}")
    
    async def _context_update_loop(self):
        """Background loop to update OS context"""
        while self.running:
            try:
                await self._update_os_context()
                await asyncio.sleep(self.context_update_interval)
            except Exception as e:
                logger.error(f"Error updating OS context: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _update_os_context(self):
        """Update OS context data"""
        try:
            # Update process information
            self.os_context.processes = await self._get_process_info()
            
            # Update memory usage
            self.os_context.memory_usage = await self._get_memory_info()
            
            # Update CPU usage
            self.os_context.cpu_usage = await self._get_cpu_usage()
            
            # Update disk usage
            self.os_context.disk_usage = await self._get_disk_usage()
            
            # Update network info
            self.os_context.network_info = await self._get_network_info()
            
            # Update active windows
            self.os_context.active_windows = await self._get_active_windows()
            
            # Update running applications
            self.os_context.running_applications = await self._get_running_applications()
            
            # Update timestamp
            import datetime
            self.os_context.last_updated = datetime.datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating OS context: {e}")
    
    async def _get_process_info(self) -> List[Dict[str, Any]]:
        """Get current process information"""
        logger.debug("Starting process info retrieval...")
        try:
            result = await asyncio.create_subprocess_exec(
                'ps', 'aux', '--sort=-pcpu',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            logger.debug(f"ps command return code: {result.returncode}")
            if stderr:
                logger.debug(f"ps stderr: {stderr.decode()}")
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                logger.debug(f"ps output lines: {len(lines)}")
                
                if len(lines) > 1:
                    header = lines[0]
                    logger.debug(f"ps header: {header}")
                    
                    processes = []
                    for i, line in enumerate(lines[1:21]):  # Top 20 processes (skip header)
                        parts = line.split(None, 10)
                        logger.debug(f"Processing line {i}: {len(parts)} parts")
                        if len(parts) >= 11:
                            processes.append({
                                'user': parts[0],
                                'pid': parts[1],
                                'cpu': parts[2],
                                'memory': parts[3],
                                'vsz': parts[4],
                                'rss': parts[5],
                                'tty': parts[6],
                                'stat': parts[7],
                                'start': parts[8],
                                'time': parts[9],
                                'command': parts[10]
                            })
                    
                    logger.debug(f"✅ Found {len(processes)} processes")
                    return processes
                else:
                    logger.warning("No process lines found")
            else:
                logger.error(f"ps command failed with return code {result.returncode}")
                if stderr:
                    logger.error(f"ps stderr: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
        return []
    
    async def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information"""
        logger.debug("Starting memory info retrieval...")
        
        # Method 1: Use /proc/meminfo (most reliable)
        try:
            logger.debug("Trying /proc/meminfo method...")
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_data = {}
            for line in meminfo.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    # Extract numeric value in kB
                    value = value.strip().replace(' kB', '')
                    if value.isdigit():
                        mem_data[key.strip()] = int(value) * 1024  # Convert to bytes
            
            if 'MemTotal' in mem_data:
                total = mem_data['MemTotal']
                available = mem_data.get('MemAvailable', mem_data.get('MemFree', 0))
                free = mem_data.get('MemFree', 0)
                buffers = mem_data.get('Buffers', 0)
                cached = mem_data.get('Cached', 0)
                shared = mem_data.get('Shmem', 0)
                used = total - available
                
                result = {
                    'total': self._format_bytes(total),
                    'used': self._format_bytes(used),
                    'free': self._format_bytes(free),
                    'available': self._format_bytes(available),
                    'buffers': self._format_bytes(buffers),
                    'cached': self._format_bytes(cached),
                    'shared': self._format_bytes(shared),
                    'total_bytes': total,
                    'used_bytes': used,
                    'available_bytes': available,
                    'usage_percent': (used / total) * 100 if total > 0 else 0
                }
                logger.debug(f"✅ /proc/meminfo successful: {result['total']} total, {result['used']} used")
                return result
            else:
                logger.warning("No MemTotal found in /proc/meminfo")
                
        except Exception as e:
            logger.warning(f"Failed to read /proc/meminfo: {e}")
        
        # Method 2: Fallback to free command
        try:
            logger.debug("Trying free command method...")
            result = await asyncio.create_subprocess_exec(
                'free', '-b',  # Get bytes instead of human-readable
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                logger.debug(f"Free command output lines: {len(lines)}")
                
                if len(lines) >= 2:
                    mem_line = lines[1].split()
                    logger.debug(f"Memory line: {mem_line}")
                    
                    if len(mem_line) >= 7:
                        total = int(mem_line[1])
                        used = int(mem_line[2])
                        free = int(mem_line[3])
                        shared = int(mem_line[4]) if len(mem_line) > 4 else 0
                        buff_cache = int(mem_line[5]) if len(mem_line) > 5 else 0
                        available = int(mem_line[6]) if len(mem_line) > 6 else 0
                        
                        result = {
                            'total': self._format_bytes(total),
                            'used': self._format_bytes(used),
                            'free': self._format_bytes(free),
                            'available': self._format_bytes(available),
                            'shared': self._format_bytes(shared),
                            'buff_cache': self._format_bytes(buff_cache),
                            'total_bytes': total,
                            'used_bytes': used,
                            'available_bytes': available,
                            'usage_percent': (used / total) * 100 if total > 0 else 0
                        }
                        logger.debug(f"✅ free command successful: {result['total']} total, {result['used']} used")
                        return result
                    else:
                        logger.warning(f"Not enough columns in free output: {len(mem_line)}")
                else:
                    logger.warning(f"Not enough lines in free output: {len(lines)}")
            else:
                logger.warning(f"free command failed with return code {result.returncode}: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Error running free command: {e}")
        
        # Method 3: Simple fallback - try to get basic info from /proc/stat
        try:
            logger.debug("Trying basic /proc/stat method...")
            # This is a very basic fallback - not ideal but better than nothing
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('cpu'):
                        # At least we can indicate system is responsive
                        return {
                            'total': 'Unknown',
                            'used': 'Unknown', 
                            'free': 'Unknown',
                            'available': 'Unknown',
                            'error': 'Memory info unavailable - system responsive'
                        }
        except Exception as e:
            logger.error(f"Even basic system check failed: {e}")
        
        logger.error("All memory retrieval methods failed")
        return {
            'total': 'Error',
            'used': 'Error',
            'free': 'Error', 
            'available': 'Error',
            'error': 'Memory retrieval failed'
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"
    
    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            result = await asyncio.create_subprocess_exec(
                'top', '-bn1',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                for line in lines:
                    if '%Cpu(s):' in line:
                        # Parse CPU usage from top output
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'us' in part:
                                return float(parts[i].replace('%', '').replace('us', ''))
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
        return 0.0
    
    async def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            result = await asyncio.create_subprocess_exec(
                'df', '-h',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')[1:]  # Skip header
                disks = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        disks.append({
                            'filesystem': parts[0],
                            'size': parts[1],
                            'used': parts[2],
                            'available': parts[3],
                            'use_percent': parts[4],
                            'mounted_on': parts[5]
                        })
                return {'disks': disks}
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
        return {}
    
    async def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ip', 'addr', 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                output = stdout.decode()
                # Parse network interfaces (simplified)
                interfaces = []
                current_interface = None
                
                for line in output.split('\n'):
                    if line and not line.startswith(' '):
                        # New interface
                        parts = line.split()
                        if len(parts) >= 2:
                            current_interface = {
                                'name': parts[1].rstrip(':'),
                                'state': 'UP' if 'UP' in line else 'DOWN',
                                'addresses': []
                            }
                            interfaces.append(current_interface)
                    elif current_interface and 'inet ' in line:
                        # IP address
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            current_interface['addresses'].append(parts[1])
                
                return {'interfaces': interfaces}
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
        return {}
    
    async def _get_active_windows(self) -> List[Dict[str, Any]]:
        """Get active windows information"""
        logger.debug("Starting active windows detection...")
        
        # Method 1: Try wmctrl
        try:
            result = await asyncio.create_subprocess_exec(
                'wmctrl', '-l',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            logger.debug(f"wmctrl return code: {result.returncode}")
            if stderr:
                logger.debug(f"wmctrl stderr: {stderr.decode()}")
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                logger.debug(f"wmctrl output lines: {len(lines)}")
                
                windows = []
                for line in lines:
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append({
                                'id': parts[0],
                                'desktop': parts[1],
                                'pid': parts[2],
                                'title': parts[3]
                            })
                
                logger.debug(f"✅ Found {len(windows)} windows via wmctrl")
                return windows
        except Exception as e:
            logger.debug(f"wmctrl not available or error: {e}")
        
        # Method 2: Fallback - try to use xwininfo with xdotool
        try:
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'search', '--onlyvisible', '--name', '.',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                window_ids = stdout.decode().strip().split('\n')
                logger.debug(f"xdotool found {len(window_ids)} window IDs")
                
                windows = []
                for window_id in window_ids[:10]:  # Limit to 10 windows
                    if window_id.strip():
                        try:
                            # Get window title
                            title_result = await asyncio.create_subprocess_exec(
                                'xdotool', 'getwindowname', window_id,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            title_stdout, _ = await title_result.communicate()
                            
                            if title_result.returncode == 0:
                                title = title_stdout.decode().strip()
                                windows.append({
                                    'id': window_id,
                                    'desktop': '0',
                                    'pid': 'unknown',
                                    'title': title
                                })
                        except Exception as e:
                            logger.debug(f"Error getting window title for {window_id}: {e}")
                
                logger.debug(f"✅ Found {len(windows)} windows via xdotool")
                return windows
                
        except Exception as e:
            logger.debug(f"xdotool not available or error: {e}")
        
        logger.debug("No window detection method available")
        return []
    
    async def _get_running_applications(self) -> List[str]:
        """Get list of running applications"""
        logger.debug("Starting running applications detection...")
        try:
            # Get unique application names from processes
            processes = await self._get_process_info()
            logger.debug(f"Got {len(processes)} processes for app detection")
            
            apps = set()
            scientific_apps = {
                'jupyter', 'jupyter-lab', 'jupyter-notebook', 'jupyterlab',
                'rstudio', 'rserver', 'r', 'Rscript',
                'python', 'python3', 'spyder', 'spyder3',
                'octave', 'octave-gui',
                'qgis', 'grass', 'fiji', 'imagej',
                'firefox', 'chrome', 'chromium',
                'thunar', 'nautilus', 'dolphin'
            }
            
            for proc in processes:
                command = proc.get('command', '')
                logger.debug(f"Processing command: {command[:50]}...")
                
                # Extract application name from command
                if command:
                    parts = command.split()
                    if parts:
                        app_name = parts[0]
                        base_name = os.path.basename(app_name)
                        
                        # Skip system processes that start with [
                        if not base_name.startswith('['):
                            # Add the base name
                            apps.add(base_name)
                            
                            # Check for scientific applications specifically
                            # Check both the base name and the full command line
                            command_lower = command.lower()
                            base_lower = base_name.lower()
                            
                            for sci_app in scientific_apps:
                                # Check if sci_app is in the base name
                                if sci_app in base_lower:
                                    apps.add(sci_app)
                                    logger.debug(f"Found scientific app in base name: {sci_app}")
                                # Also check if sci_app is anywhere in the command line
                                elif sci_app in command_lower:
                                    apps.add(sci_app)
                                    logger.debug(f"Found scientific app in command line: {sci_app}")
                                    
                            # Special handling for JupyterLab variations
                            if any(x in command_lower for x in ['jupyter-lab', 'jupyterlab', 'jupyter lab']):
                                apps.add('jupyter')
                                apps.add('jupyterlab')
                                logger.debug(f"Found JupyterLab in command: {command}")
                                
                            # Special handling for RStudio variations
                            if any(x in command_lower for x in ['rstudio', 'rserver']):
                                apps.add('rstudio')
                                logger.debug(f"Found RStudio in command: {command}")
                                
                            # Special handling for Python variations
                            if any(x in command_lower for x in ['python', 'python3']):
                                apps.add('python')
                                logger.debug(f"Found Python in command: {command}")
            
            result = sorted(list(apps))
            logger.debug(f"✅ Found {len(result)} running applications: {result[:10]}")
            return result
        except Exception as e:
            logger.error(f"Error getting running applications: {e}")
        return []
    
    def get_os_context(self) -> OSContextData:
        """Get current OS context"""
        return self.os_context
    
    async def force_memory_update(self) -> Dict[str, Any]:
        """Force an immediate memory info update for debugging"""
        logger.info("🔄 Forcing memory info update...")
        memory_info = await self._get_memory_info()
        self.os_context.memory_usage = memory_info
        logger.info(f"✅ Memory info updated: {memory_info}")
        return memory_info
    
    def get_context_summary(self) -> str:
        """Get a human-readable summary of the OS context"""
        ctx = self.os_context
        
        # Format memory information
        memory_info = ctx.memory_usage
        if memory_info and 'total' in memory_info:
            if 'error' in memory_info:
                memory_str = f"❌ {memory_info['error']}"
            elif memory_info['total'] == 'Unknown':
                memory_str = "❓ Memory info unavailable"
            elif memory_info['total'] == 'Error':
                memory_str = "❌ Memory retrieval failed"
            else:
                usage_percent = memory_info.get('usage_percent', 0)
                status_icon = "🟢" if usage_percent < 80 else "🟡" if usage_percent < 90 else "🔴"
                memory_str = f"{status_icon} {memory_info['used']} / {memory_info['total']} ({usage_percent:.1f}%)"
        else:
            memory_str = "❌ N/A"
        
        # Format disk usage
        disk_info = ctx.disk_usage.get('disks', [])
        disk_count = len(disk_info)
        
        # Get primary disk usage if available
        primary_disk = ""
        if disk_info:
            root_disk = next((d for d in disk_info if d.get('mounted_on') == '/'), None)
            if root_disk:
                primary_disk = f" (Root: {root_disk['used']} / {root_disk['size']} - {root_disk['use_percent']})"
        
        summary = f"""## DeSciOS System Context (Updated: {ctx.last_updated})

### System Resources:
- **CPU Usage**: {ctx.cpu_usage:.1f}%
- **Memory**: {memory_str}
- **Top Processes**: {len(ctx.processes)} processes tracked
- **Active Applications**: {len(ctx.running_applications)} running

### Network & Storage:
- **Network Interfaces**: {len(ctx.network_info.get('interfaces', []))} interfaces
- **Disk Usage**: {disk_count} mounted filesystems{primary_disk}

### Desktop Environment:
- **Active Windows**: {len(ctx.active_windows)} windows
- **Running Apps**: {', '.join(ctx.running_applications[:10])}{'...' if len(ctx.running_applications) > 10 else ''}

### Scientific Computing Environment:
- **JupyterLab**: {'Running' if any('jupyter' in app.lower() for app in ctx.running_applications) else 'Not detected'}
- **R/RStudio**: {'Running' if any('rstudio' in app.lower() for app in ctx.running_applications) else 'Not detected'}
- **Python**: {'Running' if any('python' in app for app in ctx.running_applications) else 'Not detected'}
"""
        return summary
    
    async def execute_os_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute an OS command and return results"""
        try:
            cmd_args = [command] + (args or [])
            result = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                'command': ' '.join(cmd_args),
                'return_code': result.returncode,
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else '',
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'command': command,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    async def get_file_context(self, path: str) -> Dict[str, Any]:
        """Get context about a file or directory"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {'error': f'Path does not exist: {path}'}
            
            stat = path_obj.stat()
            context = {
                'path': str(path_obj.absolute()),
                'name': path_obj.name,
                'type': 'directory' if path_obj.is_dir() else 'file',
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'permissions': oct(stat.st_mode)[-3:],
                'owner': stat.st_uid,
                'group': stat.st_gid
            }
            
            if path_obj.is_dir():
                try:
                    context['contents'] = [item.name for item in path_obj.iterdir()]
                except PermissionError:
                    context['contents'] = ['Permission denied']
            elif path_obj.is_file() and stat.st_size < 1024*1024:  # < 1MB
                try:
                    context['content_preview'] = path_obj.read_text(encoding='utf-8', errors='ignore')[:1000]
                except:
                    context['content_preview'] = 'Binary file or read error'
            
            return context
        except Exception as e:
            return {'error': str(e)}

# Global instance
_mcp_client_manager = None

async def get_mcp_client_manager() -> MCPClientManager:
    """Get the global MCP client manager instance"""
    global _mcp_client_manager
    if _mcp_client_manager is None:
        _mcp_client_manager = MCPClientManager()
        await _mcp_client_manager.start()
    return _mcp_client_manager

async def shutdown_mcp_client_manager():
    """Shutdown the global MCP client manager"""
    global _mcp_client_manager
    if _mcp_client_manager:
        await _mcp_client_manager.stop()
        _mcp_client_manager = None 