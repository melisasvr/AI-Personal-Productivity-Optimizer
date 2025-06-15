import json
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict
import pickle
import os

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    deadline: Optional[datetime.datetime]
    estimated_hours: float
    energy_level_required: int  # 1-10 scale
    tags: List[str]
    status: TaskStatus
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    actual_hours: Optional[float] = None

@dataclass
class ProductivitySession:
    start_time: datetime.datetime
    end_time: datetime.datetime
    tasks_completed: List[str]
    focus_score: int  # 1-10 scale
    energy_level: int  # 1-10 scale
    distractions_count: int
    tools_used: List[str]

class TaskPrioritizationAgent:
    def __init__(self):
        self.user_patterns = {}
        self.task_completion_history = []
    
    def calculate_task_score(self, task: Task, current_energy: int, current_time: datetime.datetime) -> float:
        """Calculate priority score for a task based on multiple factors"""
        score = 0
        
        # Deadline urgency (0-40 points)
        if task.deadline:
            days_until_deadline = (task.deadline - current_time).days
            if days_until_deadline <= 0:
                score += 40  # Overdue
            elif days_until_deadline <= 1:
                score += 35  # Due today/tomorrow
            elif days_until_deadline <= 3:
                score += 25  # Due this week
            elif days_until_deadline <= 7:
                score += 15  # Due next week
            else:
                score += 5   # Due later
        
        # Priority level (0-25 points)
        priority_scores = {Priority.URGENT: 25, Priority.HIGH: 20, Priority.MEDIUM: 10, Priority.LOW: 5}
        score += priority_scores.get(task.priority, 0)
        
        # Energy alignment (0-20 points)
        energy_diff = abs(current_energy - task.energy_level_required)
        score += max(0, 20 - (energy_diff * 2))
        
        # Effort vs available time (0-15 points)
        hour = current_time.hour
        if hour >= 9 and hour <= 17:  # Work hours
            if task.estimated_hours <= 2:
                score += 15  # Short tasks during work hours
            elif task.estimated_hours <= 4:
                score += 10
            else:
                score += 5
        
        return score
    
    def prioritize_tasks(self, tasks: List[Task], current_energy: int, current_time: datetime.datetime) -> List[Task]:
        """Return tasks sorted by priority score"""
        task_scores = [(task, self.calculate_task_score(task, current_energy, current_time)) 
                      for task in tasks if task.status == TaskStatus.PENDING]
        
        # Sort by score (descending)
        task_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [task for task, score in task_scores]

class FocusDistractionsAgent:
    def __init__(self):
        self.productivity_history = []
        self.focus_patterns = defaultdict(list)
        self.distraction_triggers = defaultdict(int)
    
    def log_session(self, session: ProductivitySession):
        """Log a productivity session"""
        self.productivity_history.append(session)
        
        # Update focus patterns by time of day
        hour = session.start_time.hour
        self.focus_patterns[hour].append(session.focus_score)
        
        # Track distraction triggers
        if session.distractions_count > 3:  # High distraction session
            self.distraction_triggers[hour] += 1
    
    def get_optimal_focus_time(self) -> Tuple[int, int]:
        """Find the best time window for deep work"""
        if not self.focus_patterns:
            return (9, 11)  # Default morning focus time
        
        # Calculate average focus score for each hour
        avg_focus_by_hour = {}
        for hour, scores in self.focus_patterns.items():
            avg_focus_by_hour[hour] = sum(scores) / len(scores)
        
        # Find best 2-hour window
        best_score = 0
        best_window = (9, 11)
        
        for start_hour in range(6, 20):  # 6 AM to 8 PM
            end_hour = start_hour + 2
            if end_hour <= 22:  # Don't go past 10 PM
                window_score = (avg_focus_by_hour.get(start_hour, 5) + 
                              avg_focus_by_hour.get(start_hour + 1, 5)) / 2
                if window_score > best_score:
                    best_score = window_score
                    best_window = (start_hour, end_hour)
        
        return best_window
    
    def suggest_break_time(self, current_time: datetime.datetime) -> bool:
        """Suggest if user should take a break"""
        hour = current_time.hour
        
        # Suggest break if current hour has high distraction history
        if self.distraction_triggers.get(hour, 0) > 3:
            return True
        
        # Suggest break every 90 minutes (Pomodoro technique extended)
        # This would need session tracking to implement properly
        return False
    
    def get_distraction_mitigation_tips(self) -> List[str]:
        """Provide personalized tips to reduce distractions"""
        tips = [
            "Consider using website blockers during focus sessions",
            "Turn off non-essential notifications",
            "Use noise-cancelling headphones or white noise",
            "Keep your phone in another room or in airplane mode",
            "Prepare everything you need before starting deep work"
        ]
        
        # Add personalized tips based on patterns
        high_distraction_hours = [hour for hour, count in self.distraction_triggers.items() if count > 2]
        if high_distraction_hours:
            tips.append(f"Your most distracting hours are {high_distraction_hours}. Consider scheduling lighter tasks during these times.")
        
        return tips

class ResourceRecommendationAgent:
    def __init__(self):
        self.skill_interests = defaultdict(int)
        self.tool_effectiveness = defaultdict(list)
        self.resource_database = self._initialize_resources()
    
    def _initialize_resources(self) -> Dict:
        """Initialize a database of resources by category"""
        return {
            "productivity": [
                {"name": "Notion", "type": "tool", "description": "All-in-one workspace"},
                {"name": "Todoist", "type": "tool", "description": "Task management"},
                {"name": "Getting Things Done", "type": "book", "description": "Productivity methodology"},
            ],
            "time_management": [
                {"name": "RescueTime", "type": "tool", "description": "Time tracking"},
                {"name": "Forest", "type": "app", "description": "Focus timer with gamification"},
                {"name": "Pomodoro Timer", "type": "technique", "description": "25-minute focused work sessions"},
            ],
            "automation": [
                {"name": "Zapier", "type": "tool", "description": "Workflow automation"},
                {"name": "IFTTT", "type": "tool", "description": "Simple automation"},
                {"name": "Python scripts", "type": "skill", "description": "Custom automation solutions"},
            ],
            "learning": [
                {"name": "Coursera", "type": "platform", "description": "Online courses"},
                {"name": "YouTube", "type": "platform", "description": "Free tutorials"},
                {"name": "Stack Overflow", "type": "community", "description": "Programming Q&A"},
            ],
            # Add mappings for task tags
            "writing": [
                {"name": "Grammarly", "type": "tool", "description": "Writing assistant"},
                {"name": "Hemingway Editor", "type": "tool", "description": "Writing clarity tool"},
                {"name": "Notion", "type": "tool", "description": "Document creation and organization"},
            ],
            "project": [
                {"name": "Trello", "type": "tool", "description": "Project management boards"},
                {"name": "Asana", "type": "tool", "description": "Team project management"},
                {"name": "Monday.com", "type": "tool", "description": "Work management platform"},
            ],
            "deadline": [
                {"name": "Calendar blocking", "type": "technique", "description": "Block time for important deadlines"},
                {"name": "Todoist", "type": "tool", "description": "Deadline tracking and reminders"},
                {"name": "TimeTree", "type": "app", "description": "Shared calendar for deadlines"},
            ],
            "email": [
                {"name": "Boomerang", "type": "tool", "description": "Email scheduling and reminders"},
                {"name": "Mixmax", "type": "tool", "description": "Email productivity suite"},
                {"name": "Gmail filters", "type": "technique", "description": "Automatic email organization"},
            ],
            "communication": [
                {"name": "Slack", "type": "tool", "description": "Team communication"},
                {"name": "Microsoft Teams", "type": "tool", "description": "Video conferencing and chat"},
                {"name": "Loom", "type": "tool", "description": "Video messaging"},
            ],
            "meeting": [
                {"name": "Calendly", "type": "tool", "description": "Meeting scheduling"},
                {"name": "Zoom", "type": "tool", "description": "Video conferencing"},
                {"name": "Otter.ai", "type": "tool", "description": "Meeting transcription"},
            ],
            "preparation": [
                {"name": "MindMeister", "type": "tool", "description": "Mind mapping for preparation"},
                {"name": "Miro", "type": "tool", "description": "Collaborative whiteboard"},
                {"name": "OneNote", "type": "tool", "description": "Note organization"},
            ]
        }
    
    def track_skill_interest(self, skill: str):
        """Track user's interest in a skill"""
        self.skill_interests[skill] += 1
    
    def get_recommendations(self, task_tags: List[str], skill_goals: List[str] = None) -> List[Dict]:
        """Get personalized resource recommendations"""
        recommendations = []
        
        # Recommend based on task tags
        for tag in task_tags:
            if tag.lower() in self.resource_database:
                recommendations.extend(self.resource_database[tag.lower()])
        
        # Recommend based on skill goals
        if skill_goals:
            for skill in skill_goals:
                if skill.lower() in self.resource_database:
                    recommendations.extend(self.resource_database[skill.lower()])
        
        # If no specific recommendations found, provide general productivity tools
        if not recommendations:
            recommendations = self.resource_database["productivity"]
        
        # Remove duplicates and limit to top 5
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["name"] not in seen:
                seen.add(rec["name"])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= 5:
                    break
        
        return unique_recommendations

class WorkflowAutomationAgent:
    def __init__(self):
        self.task_patterns = defaultdict(list)
        self.repetitive_tasks = []
        self.automation_suggestions = []
    
    def analyze_task_patterns(self, tasks: List[Task]):
        """Analyze tasks for repetitive patterns"""
        # Clear previous patterns
        self.task_patterns.clear()
        self.repetitive_tasks.clear()
        
        for task in tasks:
            # Group by similar titles/descriptions
            key = self._extract_pattern_key(task.title)
            self.task_patterns[key].append(task)
        
        # Identify repetitive tasks (appearing 2+ times for demo purposes)
        for pattern, task_list in self.task_patterns.items():
            if len(task_list) >= 2:  # Lowered threshold for demo
                self.repetitive_tasks.append({
                    "pattern": pattern,
                    "frequency": len(task_list),
                    "tasks": task_list
                })
    
    def _extract_pattern_key(self, title: str) -> str:
        """Extract pattern from task title"""
        # Simple pattern extraction - in real implementation, use NLP
        words = title.lower().split()
        
        # Look for common patterns
        if "email" in words:
            return "email_tasks"
        elif "meeting" in words:
            return "meeting_tasks"
        elif "report" in words:
            return "report_tasks"
        elif "review" in words:
            return "review_tasks"
        elif "project" in words:
            return "project_tasks"
        elif "preparation" in words or "prepare" in words:
            return "preparation_tasks"
        else:
            return "other_tasks"
    
    def generate_automation_suggestions(self) -> List[Dict]:
        """Generate suggestions for automating repetitive tasks"""
        suggestions = []
        
        # Always provide some general automation suggestions if no specific patterns found
        if not self.repetitive_tasks:
            suggestions.append({
                "pattern": "general_productivity",
                "suggestion": "Set up email templates for common responses",
                "tools": ["Gmail templates", "Outlook Quick Parts"],
                "potential_time_saved": "2-3 hours/week"
            })
            suggestions.append({
                "pattern": "general_productivity",
                "suggestion": "Use calendar automation for recurring meetings",
                "tools": ["Google Calendar", "Outlook Calendar"],
                "potential_time_saved": "1-2 hours/week"
            })
        
        for repetitive_task in self.repetitive_tasks:
            pattern = repetitive_task["pattern"]
            frequency = repetitive_task["frequency"]
            
            if pattern == "email_tasks":
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": "Create email templates and use email scheduling",
                    "tools": ["Gmail templates", "Boomerang", "Mixmax"],
                    "potential_time_saved": f"{frequency * 0.5} hours/week"
                })
            elif pattern == "meeting_tasks":
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": "Use calendar automation and meeting templates",
                    "tools": ["Calendly", "Google Calendar", "Zoom"],
                    "potential_time_saved": f"{frequency * 0.25} hours/week"
                })
            elif pattern == "report_tasks":
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": "Create report templates and automate data collection",
                    "tools": ["Python scripts", "Excel macros", "Power BI"],
                    "potential_time_saved": f"{frequency * 1.0} hours/week"
                })
            elif pattern == "project_tasks":
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": "Use project templates and automated workflows",
                    "tools": ["Notion templates", "Trello automation", "Zapier"],
                    "potential_time_saved": f"{frequency * 0.75} hours/week"
                })
            elif pattern == "preparation_tasks":
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": "Create preparation checklists and templates",
                    "tools": ["Notion templates", "Todoist templates", "Google Docs"],
                    "potential_time_saved": f"{frequency * 0.5} hours/week"
                })
        
        return suggestions

class ProductivityOptimizer:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.task_agent = TaskPrioritizationAgent()
        self.focus_agent = FocusDistractionsAgent()
        self.resource_agent = ResourceRecommendationAgent()
        self.automation_agent = WorkflowAutomationAgent()
        
        self.tasks = []
        self.current_energy = 7  # Default energy level
        
        # Load user data if exists
        self._load_user_data()
    
    def add_task(self, title: str, description: str, priority: Priority, 
                 deadline: Optional[datetime.datetime] = None, estimated_hours: float = 1.0,
                 energy_level_required: int = 5, tags: List[str] = None) -> Task:
        """Add a new task"""
        task = Task(
            id=f"task_{len(self.tasks) + 1}",
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            estimated_hours=estimated_hours,
            energy_level_required=energy_level_required,
            tags=tags or [],
            status=TaskStatus.PENDING,
            created_at=datetime.datetime.now()
        )
        self.tasks.append(task)
        return task
    
    def get_daily_recommendations(self) -> Dict:
        """Get comprehensive daily recommendations"""
        current_time = datetime.datetime.now()
        
        # Get prioritized tasks
        prioritized_tasks = self.task_agent.prioritize_tasks(
            self.tasks, self.current_energy, current_time
        )
        
        # Get focus recommendations
        optimal_focus_time = self.focus_agent.get_optimal_focus_time()
        should_take_break = self.focus_agent.suggest_break_time(current_time)
        distraction_tips = self.focus_agent.get_distraction_mitigation_tips()
        
        # Get resource recommendations
        all_tags = []
        for task in prioritized_tasks[:3]:  # Top 3 tasks
            all_tags.extend(task.tags)
        
        resource_recommendations = self.resource_agent.get_recommendations(all_tags)
        
        # Get automation suggestions
        self.automation_agent.analyze_task_patterns(self.tasks)
        automation_suggestions = self.automation_agent.generate_automation_suggestions()
        
        return {
            "timestamp": current_time.isoformat(),
            "prioritized_tasks": [asdict(task) for task in prioritized_tasks[:5]],
            "focus_recommendations": {
                "optimal_focus_time": f"{optimal_focus_time[0]}:00 - {optimal_focus_time[1]}:00",
                "should_take_break": should_take_break,
                "distraction_tips": distraction_tips[:3]
            },
            "resource_recommendations": resource_recommendations,
            "automation_suggestions": automation_suggestions
        }
    
    def complete_task(self, task_id: str, actual_hours: float = None):
        """Mark a task as completed"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.datetime.now()
                if actual_hours:
                    task.actual_hours = actual_hours
                break
    
    def log_productivity_session(self, start_time: datetime.datetime, end_time: datetime.datetime,
                                tasks_completed: List[str], focus_score: int, energy_level: int,
                                distractions_count: int, tools_used: List[str] = None):
        """Log a productivity session"""
        session = ProductivitySession(
            start_time=start_time,
            end_time=end_time,
            tasks_completed=tasks_completed,
            focus_score=focus_score,
            energy_level=energy_level,
            distractions_count=distractions_count,
            tools_used=tools_used or []
        )
        self.focus_agent.log_session(session)
        self.current_energy = energy_level  # Update current energy
    
    def _save_user_data(self):
        """Save user data to file"""
        data = {
            "tasks": [asdict(task) for task in self.tasks],
            "task_agent": self.task_agent.__dict__,
            "focus_agent": self.focus_agent.__dict__,
            "resource_agent": self.resource_agent.__dict__,
            "automation_agent": self.automation_agent.__dict__,
            "current_energy": self.current_energy
        }
        
        os.makedirs("user_data", exist_ok=True)
        with open(f"user_data/{self.user_id}.json", "w") as f:
            json.dump(data, f, default=str, indent=2)
    
    def _load_user_data(self):
        """Load user data from file"""
        try:
            with open(f"user_data/{self.user_id}.json", "r") as f:
                data = json.load(f)
                
            # Reconstruct tasks
            self.tasks = []
            for task_data in data.get("tasks", []):
                # Convert string dates back to datetime objects
                if task_data.get("deadline"):
                    task_data["deadline"] = datetime.datetime.fromisoformat(task_data["deadline"])
                task_data["created_at"] = datetime.datetime.fromisoformat(task_data["created_at"])
                if task_data.get("completed_at"):
                    task_data["completed_at"] = datetime.datetime.fromisoformat(task_data["completed_at"])
                
                # Convert enums
                task_data["priority"] = Priority(task_data["priority"])
                task_data["status"] = TaskStatus(task_data["status"])
                
                self.tasks.append(Task(**task_data))
            
            self.current_energy = data.get("current_energy", 7)
            
        except FileNotFoundError:
            pass  # No existing data

# Example usage and testing
if __name__ == "__main__":
    # Initialize the productivity optimizer
    optimizer = ProductivityOptimizer("user123")
    
    # Add some sample tasks with more variety to demonstrate automation patterns
    optimizer.add_task(
        "Complete project proposal",
        "Write and review the Q2 project proposal",
        Priority.HIGH,
        datetime.datetime.now() + datetime.timedelta(days=2),
        estimated_hours=4.0,
        energy_level_required=8,
        tags=["writing", "project", "deadline"]
    )
    
    optimizer.add_task(
        "Review email inbox",
        "Go through and respond to emails",
        Priority.MEDIUM,
        estimated_hours=0.5,
        energy_level_required=3,
        tags=["email", "communication"]
    )
    
    optimizer.add_task(
        "Team meeting preparation",
        "Prepare agenda and materials for team meeting",
        Priority.MEDIUM,
        datetime.datetime.now() + datetime.timedelta(days=1),
        estimated_hours=1.0,
        energy_level_required=6,
        tags=["meeting", "preparation"]
    )
    
    # Add more tasks to show automation patterns
    optimizer.add_task(
        "Weekly project status review",
        "Review project progress and update stakeholders",
        Priority.MEDIUM,
        estimated_hours=2.0,
        energy_level_required=7,
        tags=["project", "review"]
    )
    
    optimizer.add_task(
        "Client meeting preparation",
        "Prepare materials and agenda for client presentation",
        Priority.HIGH,
        estimated_hours=1.5,
        energy_level_required=8,
        tags=["meeting", "preparation", "client"]
    )
    
    # Log a productivity session
    optimizer.log_productivity_session(
        start_time=datetime.datetime.now() - datetime.timedelta(hours=2),
        end_time=datetime.datetime.now() - datetime.timedelta(hours=1),
        tasks_completed=["task_2"],
        focus_score=8,
        energy_level=7,
        distractions_count=2,
        tools_used=["email", "calendar"]
    )
    
    # Get daily recommendations
    recommendations = optimizer.get_daily_recommendations()
    
    print("=== AI Personal Productivity Optimizer ===")
    print(f"Recommendations for {datetime.datetime.now().strftime('%Y-%m-%d')}")
    print("\n📋 TOP PRIORITY TASKS:")
    for i, task in enumerate(recommendations["prioritized_tasks"][:3], 1):
        # Get the priority name properly
        priority = task['priority']
        if hasattr(priority, 'name'):
            priority_name = priority.name
        else:
            priority_name = str(priority).replace('Priority.', '')
        print(f"{i}. {task['title']} (Priority: {priority_name}, Est: {task['estimated_hours']}h)")
    
    print(f"\n🎯 FOCUS RECOMMENDATIONS:")
    focus_rec = recommendations["focus_recommendations"]
    print(f"• Optimal focus time: {focus_rec['optimal_focus_time']}")
    print(f"• Should take break: {focus_rec['should_take_break']}")
    print("• Distraction tips:")
    for tip in focus_rec["distraction_tips"]:
        print(f"  - {tip}")
    
    print(f"\n📚 RESOURCE RECOMMENDATIONS:")
    if recommendations["resource_recommendations"]:
        for resource in recommendations["resource_recommendations"][:3]:
            print(f"• {resource['name']} ({resource['type']}): {resource['description']}")
    else:
        print("• No specific recommendations found")
    
    print(f"\n🤖 AUTOMATION SUGGESTIONS:")
    if recommendations["automation_suggestions"]:
        for suggestion in recommendations["automation_suggestions"]:
            print(f"• {suggestion['suggestion']}")
            print(f"  Tools: {', '.join(suggestion['tools'])}")
            print(f"  Time saved: {suggestion['potential_time_saved']}")
    else:
        print("• No automation suggestions found")
    
    # Save user data
    optimizer._save_user_data()
    print("\n💾 User data saved successfully!")