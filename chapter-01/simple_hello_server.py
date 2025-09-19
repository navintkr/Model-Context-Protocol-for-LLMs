#!/usr/bin/env python3
"""
Simple MCP Hello World Server Example
A basic demonstration of MCP server concepts without external dependencies.
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

class SimpleMCPServer:
    """
    A simple MCP server implementation for demonstration purposes.
    This server provides basic tools and resources to show MCP concepts.
    """
    
    def __init__(self):
        self.name = "simple-hello-server"
        self.version = "1.0.0"
        self.tools = {
            "greet": {
                "description": "Greet a user with a personalized message",
                "parameters": {
                    "name": {"type": "string", "description": "Name of the person to greet"},
                    "language": {"type": "string", "description": "Language for greeting (en, es, fr)", "default": "en"}
                }
            },
            "get_time": {
                "description": "Get the current time",
                "parameters": {}
            },
            "calculate": {
                "description": "Perform basic arithmetic calculations",
                "parameters": {
                    "operation": {"type": "string", "description": "Operation: add, subtract, multiply, divide"},
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                }
            }
        }
        
        self.resources = {
            "server_info": {
                "description": "Information about this MCP server",
                "type": "application/json"
            },
            "sample_data": {
                "description": "Sample data for testing",
                "type": "application/json"
            }
        }
    
    async def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests."""
        print(f"🔧 Executing tool: {tool_name} with parameters: {parameters}")
        
        if tool_name == "greet":
            return await self._greet_tool(parameters)
        elif tool_name == "get_time":
            return await self._get_time_tool()
        elif tool_name == "calculate":
            return await self._calculate_tool(parameters)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def handle_resource_request(self, resource_name: str) -> Dict[str, Any]:
        """Handle resource access requests."""
        print(f"📁 Accessing resource: {resource_name}")
        
        if resource_name == "server_info":
            return {
                "name": self.name,
                "version": self.version,
                "description": "A simple MCP hello world server",
                "capabilities": list(self.tools.keys()),
                "resources": list(self.resources.keys()),
                "timestamp": datetime.now().isoformat()
            }
        elif resource_name == "sample_data":
            return {
                "users": [
                    {"id": 1, "name": "Alice", "role": "developer"},
                    {"id": 2, "name": "Bob", "role": "designer"},
                    {"id": 3, "name": "Charlie", "role": "manager"}
                ],
                "projects": [
                    {"id": 1, "name": "MCP Demo", "status": "active"},
                    {"id": 2, "name": "AI Assistant", "status": "planning"}
                ]
            }
        else:
            return {"error": f"Unknown resource: {resource_name}"}
    
    async def _greet_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Greet a user in the specified language."""
        name = parameters.get("name", "World")
        language = parameters.get("language", "en")
        
        greetings = {
            "en": f"Hello, {name}! Welcome to the MCP world!",
            "es": f"¡Hola, {name}! ¡Bienvenido al mundo MCP!",
            "fr": f"Bonjour, {name}! Bienvenue dans le monde MCP!"
        }
        
        greeting = greetings.get(language, greetings["en"])
        
        return {
            "greeting": greeting,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_time_tool(self) -> Dict[str, Any]:
        """Get the current time."""
        now = datetime.now()
        return {
            "current_time": now.isoformat(),
            "unix_timestamp": now.timestamp(),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "UTC"
        }
    
    async def _calculate_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic arithmetic calculations."""
        operation = parameters.get("operation")
        a = parameters.get("a")
        b = parameters.get("b")
        
        if not all([operation, a is not None, b is not None]):
            return {"error": "Missing required parameters: operation, a, b"}
        
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return {"error": "Division by zero"}
                result = a / b
            else:
                return {"error": f"Unknown operation: {operation}"}
            
            return {
                "operation": operation,
                "operands": [a, b],
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities."""
        return {
            "tools": self.tools,
            "resources": self.resources,
            "server_info": {
                "name": self.name,
                "version": self.version
            }
        }

async def demonstrate_mcp_server():
    """Demonstrate the MCP hello world server."""
    print("🚀 Simple MCP Server Demo")
    print("=" * 40)
    
    # Create server instance
    server = SimpleMCPServer()
    
    # Show server capabilities
    print("\n📋 Server Capabilities:")
    capabilities = server.get_capabilities()
    print(f"  Server: {capabilities['server_info']['name']} v{capabilities['server_info']['version']}")
    print(f"  Tools: {', '.join(capabilities['tools'].keys())}")
    print(f"  Resources: {', '.join(capabilities['resources'].keys())}")
    
    # Test tools
    print("\n🔧 Testing Tools:")
    
    # Test greet tool
    result = await server.handle_tool_call("greet", {"name": "Alice", "language": "en"})
    print(f"  Greet (English): {result['greeting']}")
    
    result = await server.handle_tool_call("greet", {"name": "Carlos", "language": "es"})
    print(f"  Greet (Spanish): {result['greeting']}")
    
    # Test time tool
    result = await server.handle_tool_call("get_time", {})
    print(f"  Current Time: {result['formatted_time']}")
    
    # Test calculator
    result = await server.handle_tool_call("calculate", {"operation": "add", "a": 15, "b": 27})
    print(f"  Calculate (15 + 27): {result['result']}")
    
    result = await server.handle_tool_call("calculate", {"operation": "multiply", "a": 8, "b": 7})
    print(f"  Calculate (8 × 7): {result['result']}")
    
    # Test resources
    print("\n📁 Testing Resources:")
    
    # Test server info resource
    result = await server.handle_resource_request("server_info")
    print(f"  Server Info: {result['description']}")
    print(f"  Capabilities: {', '.join(result['capabilities'])}")
    
    # Test sample data resource
    result = await server.handle_resource_request("sample_data")
    print(f"  Sample Data: {len(result['users'])} users, {len(result['projects'])} projects")
    
    # Test error handling
    print("\n❌ Testing Error Handling:")
    
    # Unknown tool
    result = await server.handle_tool_call("unknown_tool", {})
    print(f"  Unknown Tool: {result.get('error', 'No error')}")
    
    # Division by zero
    result = await server.handle_tool_call("calculate", {"operation": "divide", "a": 10, "b": 0})
    print(f"  Division by Zero: {result.get('error', 'No error')}")
    
    # Unknown resource
    result = await server.handle_resource_request("unknown_resource")
    print(f"  Unknown Resource: {result.get('error', 'No error')}")
    
    print("\n✅ Simple MCP Server Demo Complete!")

if __name__ == "__main__":
    asyncio.run(demonstrate_mcp_server())

