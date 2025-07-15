# MCP Integration for DeSciOS Assistant

This document describes the Model Context Protocol (MCP) integration in the DeSciOS Assistant, which provides **strictly OS-context-aware** capabilities for real-time system monitoring and management.

## Overview

The MCP integration transforms the DeSciOS Assistant from a simple chat interface into a **truly OS-aware AI assistant** that can:

- Monitor system resources in real-time
- Manage processes and applications
- Access filesystem context
- Interact with desktop environment
- Execute system commands safely
- Provide contextual system information

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DeSciOS Assistant (main.py)                  │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │   GTK UI       │  │   Ollama LLM     │  │   MCP Client    │  │
│  │   Chat Widget  │  │   Integration    │  │   Manager       │  │
│  └────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP Client Manager                        │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │   OS Context   │  │   Process Mon    │  │   File System   │  │
│  │   Monitoring   │  │   & Management   │  │   Access        │  │
│  └────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP OS Server                             │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │   Tools        │  │   Resources      │  │   Prompts       │  │
│  │   - sys_info   │  │   - system info  │  │   - sys_analysis│  │
│  │   - processes  │  │   - processes    │  │   - troubleshoot│  │
│  │   - launch_app │  │   - desktop env  │  │   - app_launch  │  │
│  │   - execute    │  │   - applications │  │                 │  │
│  └────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. MCP Client Manager (`mcp_client.py`)

The `MCPClientManager` is the core component that provides:

- **Real-time OS monitoring**: Continuous updates of system state
- **Process management**: Monitor and control running processes
- **Resource tracking**: CPU, memory, disk, and network usage
- **Desktop integration**: Window management and application state
- **Command execution**: Safe system command execution
- **File system context**: File and directory information

### 2. MCP OS Server (`mcp_os_server.py`)

The MCP server exposes OS capabilities through:

#### Tools:
- `get_system_info()`: Comprehensive system information
- `get_top_processes()`: Process monitoring by CPU usage
- `get_process_by_name()`: Find processes by name
- `kill_process()`: Terminate processes safely
- `execute_command()`: Run whitelisted system commands
- `get_desktop_info()`: Desktop environment information
- `launch_application()`: Start scientific applications

#### Resources:
- `os://system/info`: System hardware and resource information
- `os://processes/top`: Top processes by CPU usage
- `os://desktop/environment`: Desktop environment details
- `os://applications/scientific`: Available scientific applications

#### Prompts:
- `system_analysis_prompt()`: Generate system analysis prompts
- `process_troubleshooting_prompt()`: Create troubleshooting guides
- `application_launcher_prompt()`: Application launch assistance

### 3. Main Integration (`main.py`)

The main DeSciOS Assistant integrates MCP through:

- **Async initialization**: MCP client manager starts with the application
- **Context-aware prompts**: System context included in LLM prompts
- **Query routing**: Automatic detection of system-related queries
- **Real-time updates**: Continuous system monitoring in background
- **UI integration**: System status messages and suggestions

## Features

### 🖥️ Real-time System Monitoring
- CPU, memory, disk, and network usage
- Process monitoring and management
- System load and performance metrics
- Desktop environment state

### 🔍 Process Management
- List top processes by resource usage
- Search processes by name
- Kill processes safely
- Monitor application states

### 🚀 Application Launcher
- Launch scientific applications
- Monitor application status
- Desktop integration
- Command execution

### 📁 File System Context
- File and directory information
- Permissions and ownership
- Content preview for small files
- Directory listings

### 🛡️ Security Features
- Whitelisted command execution
- Safe process termination
- Permission-aware operations
- Secure file access

## Usage Examples

### System Status Query
```
User: "What's the current system performance?"
```
**Response**: Real-time system metrics with CPU, memory, disk usage, and top processes.

### Process Management
```
User: "What processes are using the most CPU?"
```
**Response**: Top processes by CPU usage with detailed information.

### Application Launch
```
User: "Launch JupyterLab for data analysis"
```
**Response**: Application launch with status updates and guidance.

### Desktop Information
```
User: "What applications are currently open?"
```
**Response**: List of active windows and running applications.

## Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test MCP integration**:
   ```bash
   python3 test_mcp_integration.py
   ```

3. **Run DeSciOS Assistant**:
   ```bash
   python3 main.py
   ```

## Configuration

### MCP Client Manager Settings
- **Context update interval**: 2 seconds (configurable)
- **Process monitoring**: Top 20 processes tracked
- **Memory management**: Automatic cleanup on shutdown
- **Error handling**: Graceful fallback when MCP unavailable

### Security Configuration
- **Safe commands**: Whitelist of allowed system commands
- **Process permissions**: Respect system permissions
- **File access**: Controlled file system access
- **Command timeout**: 30-second default timeout

## Troubleshooting

### Common Issues

1. **MCP initialization fails**:
   - Check if required dependencies are installed
   - Verify system permissions
   - Check log output for specific errors

2. **System monitoring unavailable**:
   - Ensure psutil is installed
   - Check if system tools are available
   - Verify process permissions

3. **Application launch fails**:
   - Verify applications are installed
   - Check desktop environment compatibility
   - Ensure proper PATH configuration

### Debug Mode
Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Docker integration**: Container monitoring and management
- **Network monitoring**: Advanced network analysis
- **Performance alerts**: Automatic performance issue detection
- **Custom workflows**: User-defined system automation
- **Multi-node support**: Distributed system monitoring

## Contributing

When contributing to MCP integration:

1. Follow the existing architecture patterns
2. Add comprehensive error handling
3. Include security considerations
4. Update documentation
5. Add tests for new features

## License

This MCP integration is part of the DeSciOS Assistant project and follows the same license terms. 