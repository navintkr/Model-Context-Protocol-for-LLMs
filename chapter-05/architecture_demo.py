#!/usr/bin/env python3
"""
MCP Architecture Demonstration
Shows core architectural principles with working code.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []

class MCPArchitectureDemo:
    """
    Demonstrates MCP architectural principles:
    1. Separation of Concerns
    2. Protocol-First Design
    3. Bidirectional Communication
    4. Capability-Based Security
    5. Composability
    """
    
    def __init__(self, server_name: str, capabilities: Set[str] = None):
        self.server_name = server_name
        self.capabilities = capabilities or {"tasks", "notifications", "analytics"}
        
        # Data storage
        self.tasks: Dict[str, Task] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.event_subscribers: Dict[str, Set[str]] = {
            "task_created": set(),
            "task_updated": set(),
            "task_completed": set()
        }
        
        # Initialize sample data
        self._initialize_sample_data()
        
        logger.info(f"Initialized {server_name} with capabilities: {', '.join(self.capabilities)}")
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demonstration."""
        
        # Sample users
        self.users = {
            "alice": {
                "name": "Alice Johnson",
                "role": "Senior Developer",
                "skills": ["python", "javascript", "architecture"],
                "max_concurrent_tasks": 3
            },
            "bob": {
                "name": "Bob Smith", 
                "role": "UI/UX Designer",
                "skills": ["design", "prototyping", "user-research"],
                "max_concurrent_tasks": 2
            },
            "carol": {
                "name": "Carol Davis",
                "role": "Project Manager",
                "skills": ["planning", "coordination", "stakeholder-management"],
                "max_concurrent_tasks": 5
            }
        }
        
        # Sample tasks
        sample_tasks = [
            Task(
                id="task-001",
                title="Implement user authentication system",
                description="Design and implement a secure user authentication system with JWT tokens",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                created_at=datetime.now() - timedelta(days=3),
                updated_at=datetime.now() - timedelta(hours=2),
                assigned_to="alice",
                due_date=datetime.now() + timedelta(days=5),
                tags=["backend", "security", "authentication"],
                dependencies=[]
            ),
            Task(
                id="task-002",
                title="Design user onboarding flow",
                description="Create wireframes and prototypes for new user onboarding experience",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.MEDIUM,
                created_at=datetime.now() - timedelta(days=7),
                updated_at=datetime.now() - timedelta(days=1),
                assigned_to="bob",
                due_date=datetime.now() - timedelta(days=1),
                tags=["frontend", "ux", "onboarding"],
                dependencies=[]
            ),
            Task(
                id="task-003",
                title="Set up CI/CD pipeline",
                description="Configure automated testing and deployment pipeline",
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                created_at=datetime.now() - timedelta(days=2),
                updated_at=datetime.now() - timedelta(days=2),
                assigned_to=None,
                due_date=datetime.now() + timedelta(days=7),
                tags=["devops", "automation", "infrastructure"],
                dependencies=["task-001"]
            )
        ]
        
        for task in sample_tasks:
            self.tasks[task.id] = task
    
    # Principle 1: Separation of Concerns
    def get_task_data(self) -> Dict[str, Any]:
        """Resource provider - handles data access only."""
        return {
            "all_tasks": self._serialize_tasks(self.tasks.values()),
            "active_tasks": self._serialize_tasks([
                task for task in self.tasks.values()
                if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
            ]),
            "overdue_tasks": self._serialize_tasks([
                task for task in self.tasks.values()
                if task.due_date and task.due_date < datetime.now() and task.status != TaskStatus.COMPLETED
            ])
        }
    
    async def create_task(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """Tool provider - handles actions only."""
        
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority(kwargs.get("priority", 2)),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to=kwargs.get("assigned_to"),
            due_date=kwargs.get("due_date"),
            tags=kwargs.get("tags", []),
            dependencies=kwargs.get("dependencies", [])
        )
        
        self.tasks[task_id] = task
        
        # Principle 3: Bidirectional Communication - send event
        await self._send_event("task_created", {
            "task_id": task_id,
            "title": title,
            "assigned_to": task.assigned_to
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{title}' created successfully"
        }
    
    def generate_task_prompt(self, task_id: str) -> str:
        """Prompt provider - handles conversation templates only."""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        prompt = f"""Analyze the following task and provide insights:

Task Details:
- ID: {task.id}
- Title: {task.title}
- Description: {task.description}
- Status: {task.status.value}
- Priority: {task.priority.name} ({task.priority.value}/4)
- Assigned to: {task.assigned_to or 'Unassigned'}
- Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}
- Due date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}
- Tags: {', '.join(task.tags) if task.tags else 'None'}

Please provide:
1. Current status assessment
2. Risk factors and blockers
3. Recommendations for next steps
"""
        
        return prompt
    
    # Principle 2: Protocol-First Design
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Return available capabilities in a standardized format."""
        
        capabilities_map = {
            "tasks": [
                "create_task",
                "update_task", 
                "assign_task",
                "search_tasks"
            ],
            "resources": [
                "get_all_tasks",
                "get_active_tasks",
                "get_overdue_tasks",
                "get_user_workloads"
            ],
            "prompts": [
                "task_analysis",
                "workload_optimization",
                "project_status_report"
            ],
            "notifications": [
                "subscribe_events",
                "unsubscribe_events"
            ]
        }
        
        available_capabilities = {}
        for capability in self.capabilities:
            if capability in capabilities_map:
                available_capabilities[capability] = capabilities_map[capability]
        
        return available_capabilities
    
    # Principle 3: Bidirectional Communication
    async def _send_event(self, event_type: str, data: Dict[str, Any]):
        """Send event notifications to subscribed clients."""
        
        if event_type in self.event_subscribers:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "server": self.server_name,
                "data": data
            }
            
            logger.info(f"Event: {event_type} - {data}")
            
            # In a real implementation, this would send to actual subscribers
            for subscriber in self.event_subscribers[event_type]:
                logger.info(f"  → Notifying subscriber: {subscriber}")
    
    def subscribe_to_events(self, client_id: str, event_types: List[str]) -> Dict[str, Any]:
        """Allow clients to subscribe to events."""
        
        subscribed_events = []
        for event_type in event_types:
            if event_type in self.event_subscribers:
                self.event_subscribers[event_type].add(client_id)
                subscribed_events.append(event_type)
        
        return {
            "success": True,
            "client_id": client_id,
            "subscribed_events": subscribed_events,
            "message": f"Subscribed to {len(subscribed_events)} event types"
        }
    
    # Principle 4: Capability-Based Security
    def check_capability_access(self, client_id: str, capability: str) -> bool:
        """Check if a client has access to a specific capability."""
        
        # In a real implementation, this would check actual permissions
        # For demo, we'll allow access to capabilities the server provides
        return capability in self.capabilities
    
    def get_client_permissions(self, client_id: str) -> Dict[str, Any]:
        """Get the specific permissions for a client."""
        
        # In a real implementation, this would be based on authentication
        # For demo, we'll return the server's capabilities
        return {
            "client_id": client_id,
            "allowed_capabilities": list(self.capabilities),
            "permissions": {
                "read_tasks": True,
                "create_tasks": True,
                "update_tasks": True,
                "delete_tasks": False,  # Example of restricted permission
                "admin_functions": False
            }
        }
    
    # Principle 5: Composability
    def compose_with_other_server(self, other_server: 'MCPArchitectureDemo') -> Dict[str, Any]:
        """Demonstrate how servers can be composed together."""
        
        combined_capabilities = self.capabilities.union(other_server.capabilities)
        
        # Example: Combine task data from both servers
        combined_tasks = {}
        combined_tasks.update(self.tasks)
        combined_tasks.update(other_server.tasks)
        
        return {
            "composition_result": True,
            "server1": self.server_name,
            "server2": other_server.server_name,
            "combined_capabilities": list(combined_capabilities),
            "total_tasks": len(combined_tasks),
            "message": f"Successfully composed {self.server_name} with {other_server.server_name}"
        }
    
    # Analytics and reporting
    def calculate_analytics(self) -> Dict[str, Any]:
        """Calculate various analytics about the task system."""
        
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {"total_tasks": 0, "message": "No tasks available"}
        
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        overdue_tasks = len([
            t for t in self.tasks.values()
            if t.due_date and t.due_date < datetime.now() and t.status != TaskStatus.COMPLETED
        ])
        
        # User workload analysis
        user_workloads = {}
        for user_id in self.users:
            user_tasks = [task for task in self.tasks.values() if task.assigned_to == user_id]
            active_tasks = [task for task in user_tasks if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
            
            user_workloads[user_id] = {
                "name": self.users[user_id]["name"],
                "total_tasks": len(user_tasks),
                "active_tasks": len(active_tasks),
                "completed_tasks": len([t for t in user_tasks if t.status == TaskStatus.COMPLETED])
            }
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / total_tasks * 100,
            "overdue_tasks": overdue_tasks,
            "user_workloads": user_workloads,
            "priority_distribution": {
                priority.name: len([t for t in self.tasks.values() if t.priority == priority])
                for priority in TaskPriority
            }
        }
    
    def generate_dependency_graph(self) -> str:
        """Generate a simple dependency graph representation."""
        
        graph_lines = ["Task Dependency Graph:"]
        
        for task in self.tasks.values():
            status_icon = {
                TaskStatus.COMPLETED: "✅",
                TaskStatus.IN_PROGRESS: "🔄", 
                TaskStatus.PENDING: "⏳",
                TaskStatus.BLOCKED: "🚫"
            }.get(task.status, "❓")
            
            graph_lines.append(f"  {status_icon} {task.title} ({task.id})")
            
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id in self.tasks:
                        dep_task = self.tasks[dep_id]
                        dep_status = "✅" if dep_task.status == TaskStatus.COMPLETED else "⏳"
                        graph_lines.append(f"    ↳ depends on: {dep_status} {dep_task.title}")
                    else:
                        graph_lines.append(f"    ↳ depends on: ❌ {dep_id} (not found)")
        
        return "\n".join(graph_lines)
    
    # Utility methods
    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Serialize a task to a dictionary."""
        task_dict = asdict(task)
        task_dict["status"] = task.status.value
        task_dict["priority"] = task.priority.value
        task_dict["priority_name"] = task.priority.name
        task_dict["created_at"] = task.created_at.isoformat()
        task_dict["updated_at"] = task.updated_at.isoformat()
        if task.due_date:
            task_dict["due_date"] = task.due_date.isoformat()
        return task_dict
    
    def _serialize_tasks(self, tasks) -> List[Dict[str, Any]]:
        """Serialize a collection of tasks."""
        return [self._serialize_task(task) for task in tasks]

async def demonstrate_mcp_architecture():
    """
    Comprehensive demonstration of MCP architectural principles.
    """
    
    print("🏗️  MCP Architecture Principles Demonstration")
    print("=" * 60)
    
    # Create two servers with different capabilities
    task_server = MCPArchitectureDemo("task-server", {"tasks", "notifications"})
    analytics_server = MCPArchitectureDemo("analytics-server", {"analytics", "notifications"})
    
    print(f"\n✅ Created servers:")
    print(f"   - {task_server.server_name}: {', '.join(task_server.capabilities)}")
    print(f"   - {analytics_server.server_name}: {', '.join(analytics_server.capabilities)}")
    
    # Principle 1: Separation of Concerns
    print(f"\n📋 Principle 1: Separation of Concerns")
    print("   Different interfaces handle different responsibilities:")
    
    # Resource access
    task_data = task_server.get_task_data()
    print(f"   - Resource Provider: {len(task_data['all_tasks'])} total tasks")
    print(f"   - Resource Provider: {len(task_data['active_tasks'])} active tasks")
    
    # Tool execution
    new_task_result = await task_server.create_task(
        "Write unit tests",
        "Add comprehensive unit tests for the authentication module",
        priority=3,
        tags=["testing", "backend"]
    )
    print(f"   - Tool Provider: {new_task_result['message']}")
    
    # Prompt generation
    prompt = task_server.generate_task_prompt("task-001")
    print(f"   - Prompt Provider: Generated analysis prompt ({len(prompt)} characters)")
    
    # Principle 2: Protocol-First Design
    print(f"\n🔌 Principle 2: Protocol-First Design")
    print("   Standardized capability discovery:")
    
    task_capabilities = task_server.get_capabilities()
    analytics_capabilities = analytics_server.get_capabilities()
    
    for server_name, capabilities in [("task-server", task_capabilities), ("analytics-server", analytics_capabilities)]:
        print(f"   - {server_name}:")
        for capability_type, methods in capabilities.items():
            print(f"     • {capability_type}: {len(methods)} methods")
    
    # Principle 3: Bidirectional Communication
    print(f"\n📡 Principle 3: Bidirectional Communication")
    print("   Event subscription and notifications:")
    
    # Subscribe to events
    subscription_result = task_server.subscribe_to_events("client-001", ["task_created", "task_updated"])
    print(f"   - {subscription_result['message']}")
    
    # Create a task (will trigger event)
    await task_server.create_task(
        "Deploy to production",
        "Deploy the latest version to production environment",
        priority=4,
        assigned_to="carol"
    )
    
    # Principle 4: Capability-Based Security
    print(f"\n🔒 Principle 4: Capability-Based Security")
    print("   Permission checking and capability access:")
    
    client_permissions = task_server.get_client_permissions("client-001")
    print(f"   - Client permissions: {len(client_permissions['allowed_capabilities'])} capabilities")
    
    # Check specific capability access
    can_create = task_server.check_capability_access("client-001", "tasks")
    can_admin = task_server.check_capability_access("client-001", "admin")
    print(f"   - Can create tasks: {can_create}")
    print(f"   - Can access admin functions: {can_admin}")
    
    # Principle 5: Composability
    print(f"\n🔗 Principle 5: Composability")
    print("   Server composition and capability aggregation:")
    
    composition_result = task_server.compose_with_other_server(analytics_server)
    print(f"   - {composition_result['message']}")
    print(f"   - Combined capabilities: {len(composition_result['combined_capabilities'])}")
    print(f"   - Total tasks across servers: {composition_result['total_tasks']}")
    
    # Analytics demonstration
    print(f"\n📊 Analytics and Insights:")
    analytics = task_server.calculate_analytics()
    print(f"   - Completion rate: {analytics['completion_rate']:.1f}%")
    print(f"   - Overdue tasks: {analytics['overdue_tasks']}")
    print(f"   - Team workload distribution:")
    for user_id, workload in analytics['user_workloads'].items():
        print(f"     • {workload['name']}: {workload['active_tasks']} active tasks")
    
    # Dependency graph
    print(f"\n🔗 Task Dependencies:")
    dependency_graph = task_server.generate_dependency_graph()
    print(dependency_graph)
    
    print(f"\n✨ Architecture Benefits Demonstrated:")
    print("   ✅ Modular design with clear separation of concerns")
    print("   ✅ Standardized protocol for interoperability")
    print("   ✅ Real-time event-driven communication")
    print("   ✅ Fine-grained capability-based security")
    print("   ✅ Composable systems that work together")
    print("   ✅ Scalable architecture for complex AI systems")

if __name__ == "__main__":
    asyncio.run(demonstrate_mcp_architecture())

