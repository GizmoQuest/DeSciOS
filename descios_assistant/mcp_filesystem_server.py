#!/usr/bin/env python3
"""
MCP Filesystem Server for DeSciOS

This server provides filesystem operations and file context for the DeSciOS assistant.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("DeSciOS Filesystem Server")

class FileInfo(BaseModel):
    """File information data structure"""
    path: str
    name: str
    size: int
    is_directory: bool
    permissions: str
    modified_time: float
    owner: str

class DirectoryListing(BaseModel):
    """Directory listing data structure"""
    path: str
    files: List[FileInfo]
    total_files: int
    total_directories: int

@mcp.tool()
def list_directory(path: str = ".") -> DirectoryListing:
    """List contents of a directory"""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"Path {path} does not exist")
        
        files = []
        total_files = 0
        total_directories = 0
        
        for item in path_obj.iterdir():
            try:
                stat = item.stat()
                file_info = FileInfo(
                    path=str(item),
                    name=item.name,
                    size=stat.st_size,
                    is_directory=item.is_dir(),
                    permissions=oct(stat.st_mode)[-3:],
                    modified_time=stat.st_mtime,
                    owner="unknown"  # Would need pwd module for full implementation
                )
                files.append(file_info)
                
                if item.is_dir():
                    total_directories += 1
                else:
                    total_files += 1
                    
            except (PermissionError, OSError):
                continue
        
        return DirectoryListing(
            path=str(path_obj),
            files=files,
            total_files=total_files,
            total_directories=total_directories
        )
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        raise

@mcp.tool()
def get_file_info(path: str) -> FileInfo:
    """Get information about a specific file"""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        
        stat = path_obj.stat()
        return FileInfo(
            path=str(path_obj),
            name=path_obj.name,
            size=stat.st_size,
            is_directory=path_obj.is_dir(),
            permissions=oct(stat.st_mode)[-3:],
            modified_time=stat.st_mtime,
            owner="unknown"
        )
    except Exception as e:
        logger.error(f"Error getting file info for {path}: {e}")
        raise

@mcp.tool()
def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read contents of a text file"""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        
        if path_obj.is_dir():
            raise IsADirectoryError(f"{path} is a directory")
        
        # Security: Only allow reading files in safe directories
        safe_dirs = ["/home", "/opt/descios_assistant", "/tmp"]
        if not any(str(path_obj).startswith(safe_dir) for safe_dir in safe_dirs):
            raise PermissionError(f"Access to {path} not allowed")
        
        with open(path_obj, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise

@mcp.tool()
def write_file(path: str, content: str, encoding: str = "utf-8") -> dict:
    """Write content to a file"""
    try:
        path_obj = Path(path).resolve()
        
        # Security: Only allow writing to safe directories
        safe_dirs = ["/home", "/opt/descios_assistant", "/tmp"]
        if not any(str(path_obj).startswith(safe_dir) for safe_dir in safe_dirs):
            return {
                "success": False,
                "error": f"Writing to {path} not allowed"
            }
        
        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path_obj, 'w', encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(path_obj),
            "size": len(content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def create_directory(path: str) -> dict:
    """Create a directory"""
    try:
        path_obj = Path(path).resolve()
        
        # Security: Only allow creating directories in safe locations
        safe_dirs = ["/home", "/opt/descios_assistant", "/tmp"]
        if not any(str(path_obj).startswith(safe_dir) for safe_dir in safe_dirs):
            return {
                "success": False,
                "error": f"Creating directory at {path} not allowed"
            }
        
        path_obj.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(path_obj),
            "created": not path_obj.exists()  # False if it already existed
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def delete_file(path: str) -> dict:
    """Delete a file or directory"""
    try:
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"Path {path} does not exist"
            }
        
        # Security: Only allow deleting in safe directories
        safe_dirs = ["/home", "/opt/descios_assistant", "/tmp"]
        if not any(str(path_obj).startswith(safe_dir) for safe_dir in safe_dirs):
            return {
                "success": False,
                "error": f"Deleting {path} not allowed"
            }
        
        if path_obj.is_dir():
            import shutil
            shutil.rmtree(path_obj)
        else:
            path_obj.unlink()
        
        return {
            "success": True,
            "path": str(path_obj),
            "type": "directory" if path_obj.is_dir() else "file"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.resource("fs://current/directory")
def get_current_directory_resource() -> str:
    """Get current working directory as a resource"""
    try:
        cwd = Path.cwd()
        listing = list_directory(str(cwd))
        
        output = f"# Current Directory: {cwd}\n\n"
        output += f"**Total**: {listing.total_files} files, {listing.total_directories} directories\n\n"
        output += "## Contents\n\n"
        
        for file_info in listing.files:
            icon = "📁" if file_info.is_directory else "📄"
            size_str = f"{file_info.size:,} bytes" if not file_info.is_directory else ""
            output += f"- {icon} **{file_info.name}** {size_str}\n"
        
        return output
    except Exception as e:
        return f"Error getting current directory: {e}"

@mcp.resource("fs://home/directory")
def get_home_directory_resource() -> str:
    """Get home directory listing as a resource"""
    try:
        home = Path.home()
        listing = list_directory(str(home))
        
        output = f"# Home Directory: {home}\n\n"
        output += f"**Total**: {listing.total_files} files, {listing.total_directories} directories\n\n"
        output += "## Contents\n\n"
        
        for file_info in listing.files:
            icon = "📁" if file_info.is_directory else "📄"
            size_str = f"{file_info.size:,} bytes" if not file_info.is_directory else ""
            output += f"- {icon} **{file_info.name}** {size_str}\n"
        
        return output
    except Exception as e:
        return f"Error getting home directory: {e}"

def main():
    """Main entry point"""
    logger.info("Starting DeSciOS Filesystem MCP Server...")
    mcp.run()

if __name__ == "__main__":
    main() 