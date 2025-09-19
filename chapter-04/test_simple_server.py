#!/usr/bin/env python3
"""
Test client for the Simple Task Manager MCP Server
"""

import asyncio
import json
import sys
import subprocess
from mcp.client.stdio import stdio_client

async def test_simple_task_server():
    """Test the simple task manager server."""
    
    print("🧪 Testing Simple Task Manager MCP Server...\n")
    
    # Start the server as a subprocess
    server_process = subprocess.Popen([
        sys.executable, "simple_task_server.py"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Connect to the server
        async with stdio_client(server_process) as (read, write):
            # Initialize the session
            print("🔌 Connecting to server...")
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            await write.send(json.dumps(init_request))
            response = await read.recv()
            print(f"✅ Initialization response: {response}")
            
            # Test 1: List available tools
            print("\n📋 Testing tool listing...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            await write.send(json.dumps(tools_request))
            response = await read.recv()
            print(f"Tools available: {response}")
            
            # Test 2: List available resources
            print("\n📚 Testing resource listing...")
            resources_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list"
            }
            
            await write.send(json.dumps(resources_request))
            response = await read.recv()
            print(f"Resources available: {response}")
            
            # Test 3: Call a tool (list tasks)
            print("\n🔧 Testing tool call (list_tasks)...")
            call_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "list_tasks",
                    "arguments": {}
                }
            }
            
            await write.send(json.dumps(call_request))
            response = await read.recv()
            print(f"List tasks result: {response}")
            
            # Test 4: Read a resource
            print("\n📖 Testing resource reading...")
            read_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {
                    "uri": "tasks://summary"
                }
            }
            
            await write.send(json.dumps(read_request))
            response = await read.recv()
            print(f"Resource read result: {response}")
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_simple_task_server())

