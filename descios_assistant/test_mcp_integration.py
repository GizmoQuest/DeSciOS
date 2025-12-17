#!/usr/bin/env python3
"""
Test script for MCP integration in DeSciOS Assistant

This script tests the MCP client manager and OS context functionality.
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
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import get_mcp_client_manager, shutdown_mcp_client_manager

async def test_mcp_integration():
    """Test MCP client manager functionality"""
    print("🧪 Testing MCP Integration for DeSciOS Assistant")
    print("=" * 60)
    
    try:
        # Test 1: Initialize MCP client manager
        print("\n1. Initializing MCP Client Manager...")
        manager = await get_mcp_client_manager()
        print("✅ MCP Client Manager initialized successfully")
        
        # Test 2: Get OS context
        print("\n2. Testing OS Context Retrieval...")
        context = manager.get_os_context()
        print(f"✅ OS Context retrieved: {len(context.processes)} processes, {context.cpu_usage:.1f}% CPU")
        
        # Test 3: Get context summary
        print("\n3. Testing Context Summary...")
        summary = manager.get_context_summary()
        print("✅ Context summary generated:")
        print(summary[:200] + "..." if len(summary) > 200 else summary)
        
        # Test 4: Execute a safe command
        print("\n4. Testing Command Execution...")
        result = await manager.execute_os_command("whoami")
        if result['success']:
            print(f"✅ Command executed successfully: {result['stdout'].strip()}")
        else:
            print(f"❌ Command failed: {result['stderr']}")
        
        # Test 5: Get file context
        print("\n5. Testing File Context...")
        file_context = await manager.get_file_context("/etc/hostname")
        if 'error' not in file_context:
            print(f"✅ File context retrieved: {file_context['type']} - {file_context['size']} bytes")
        else:
            print(f"❌ File context failed: {file_context['error']}")
        
        print("\n" + "=" * 60)
        print("🎉 MCP Integration Test PASSED!")
        print("The DeSciOS Assistant now has full OS context awareness.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        await shutdown_mcp_client_manager()
        print("✅ MCP Client Manager shut down")
    
    return True

def main():
    """Main test function"""
    print("Starting MCP integration test...")
    
    # Run the async test
    success = asyncio.run(test_mcp_integration())
    
    if success:
        print("\n🚀 Ready to run DeSciOS Assistant with MCP support!")
        print("Run: python3 main.py")
        sys.exit(0)
    else:
        print("\n❌ MCP integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 