#!/usr/bin/env python3
"""
Simplified MCP Task Manager Server
Demonstrates the core MCP interfaces with working code.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import MCP components
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt, TextContent

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    created_at: str
    assigned_to: str = None

class SimpleTaskServer:
    """A simple MCP server demonstrating all major interfaces."""
    
    def __init__(self):
        self.server = Server("simple-task-manager")
        self.tasks: Dict[str, Task] = {}
        self.next_id = 1
        
        # Create some sample tasks
        self._create_sample_tasks()
        
        # Register MCP interfaces
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _create_sample_tasks(self):
        """Create sample tasks for demonstration."""
        tasks = [
            Task("1", "Setup project", "Initialize the project structure", 
                 TaskStatus.COMPLETED, datetime.now().isoformat(), "alice"),
            Task("2", "Write documentation", "Create user documentation", 
                 TaskStatus.IN_PROGRESS, datetime.now().isoformat(), "bob"),
            Task("3", "Add tests", "Write unit tests", 
                 TaskStatus.PENDING, datetime.now().isoformat())
        ]
        
        for task in tasks:
            self.tasks[task.id] = task
        
        self.next_id = 4
    
    def _register_tools(self):
        """Register tool providers."""
        
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="create_task",
                    description="Create a new task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "assigned_to": {"type": "string"}
                        },
                        "required": ["title", "description"]
                    }
                ),
                Tool(
                    name="list_tasks",
                    description="List all tasks",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="update_status",
                    description="Update task status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}
                        },
                        "required": ["task_id", "status"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "create_task":
                task_id = str(self.next_id)
                self.next_id += 1
                
                task = Task(
                    id=task_id,
                    title=arguments["title"],
                    description=arguments["description"],
                    status=TaskStatus.PENDING,
                    created_at=datetime.now().isoformat(),
                    assigned_to=arguments.get("assigned_to")
                )
                
                self.tasks[task_id] = task
                
                result = {
                    "success": True,
                    "task_id": task_id,
                    "message": f"Task '{task.title}' created"
                }
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "list_tasks":
                tasks_list = []
                for task in self.tasks.values():
                    task_dict = asdict(task)
                    task_dict['status'] = task.status.value
                    tasks_list.append(task_dict)
                
                result = {
                    "tasks": tasks_list,
                    "total": len(tasks_list)
                }
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "update_status":
                task_id = arguments["task_id"]
                new_status = TaskStatus(arguments["status"])
                
                if task_id not in self.tasks:
                    raise ValueError(f"Task {task_id} not found")
                
                old_status = self.tasks[task_id].status
                self.tasks[task_id].status = new_status
                
                result = {
                    "success": True,
                    "task_id": task_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value
                }
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    def _register_resources(self):
        """Register resource providers."""
        
        @self.server.list_resources()
        async def list_resources():
            return [
                Resource(
                    uri="tasks://all",
                    name="All Tasks",
                    description="Complete list of all tasks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="tasks://summary",
                    name="Task Summary",
                    description="Summary statistics about tasks",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str):
            if uri == "tasks://all":
                tasks_data = {}
                for task_id, task in self.tasks.items():
                    task_dict = asdict(task)
                    task_dict['status'] = task.status.value
                    tasks_data[task_id] = task_dict
                
                return [TextContent(type="text", text=json.dumps(tasks_data, indent=2))]
            
            elif uri == "tasks://summary":
                total = len(self.tasks)
                completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
                in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
                pending = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
                
                summary = {
                    "total_tasks": total,
                    "completed": completed,
                    "in_progress": in_progress,
                    "pending": pending,
                    "completion_rate": f"{completed/total*100:.1f}%" if total > 0 else "0%"
                }
                
                return [TextContent(type="text", text=json.dumps(summary, indent=2))]
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    def _register_prompts(self):
        """Register prompt providers."""
        
        @self.server.list_prompts()
        async def list_prompts():
            return [
                Prompt(
                    name="task_report",
                    description="Generate a task status report",
                    arguments=[]
                ),
                Prompt(
                    name="task_summary",
                    description="Summarize a specific task",
                    arguments=[
                        {"name": "task_id", "description": "ID of the task", "required": True}
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict):
            if name == "task_report":
                total = len(self.tasks)
                completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
                
                prompt = f"""Generate a comprehensive task status report based on the following data:

Total Tasks: {total}
Completed Tasks: {completed}
Completion Rate: {completed/total*100:.1f}% if total > 0 else 0%

Recent Tasks:
"""
                for task in list(self.tasks.values())[-3:]:
                    prompt += f"- {task.title} ({task.status.value})\n"
                
                prompt += "\nPlease provide insights and recommendations based on this data."
                
                return [TextContent(type="text", text=prompt)]
            
            elif name == "task_summary":
                task_id = arguments.get("task_id")
                if not task_id or task_id not in self.tasks:
                    raise ValueError(f"Task {task_id} not found")
                
                task = self.tasks[task_id]
                prompt = f"""Provide a detailed summary of the following task:

Title: {task.title}
Description: {task.description}
Status: {task.status.value}
Assigned to: {task.assigned_to or 'Unassigned'}
Created: {task.created_at}

Please analyze the task status and provide recommendations for next steps."""
                
                return [TextContent(type="text", text=prompt)]
            
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def run(self):
        """Run the MCP server."""
        options = self.server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, options)

async def main():
    """Main function to run the server."""
    server = SimpleTaskServer()
    print("🚀 Starting Simple Task Manager MCP Server...")
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

