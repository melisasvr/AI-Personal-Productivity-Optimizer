# AI Personal Productivity Optimizer
A comprehensive AI-powered productivity system that provides intelligent task prioritization, focus optimization, resource recommendations, and workflow automation suggestions to maximize your personal productivity.

## 🚀 Features
### 📋 Smart Task Prioritization
- **Multi-factor scoring system** that considers deadlines, priority levels, energy alignment, and time availability
- **Deadline urgency calculation** with automatic overdue detection
- **Energy-based task matching** to align tasks with your current energy levels
- **Time-aware prioritization** that considers work hours and task duration

### 🎯 Focus & Distraction Management
- **Optimal focus time detection** based on your productivity patterns
- **Personalized break suggestions** using historical distraction data
- **Distraction mitigation tips** tailored to your work patterns
- **Productivity session tracking** with focus scores and energy levels

### 📚 Resource Recommendations
- **Context-aware tool suggestions** based on task tags and requirements
- **Skill-based recommendations** for learning and development
- **Productivity tool database** with categorized resources
- **Personalized filtering** based on usage patterns

### 🤖 Workflow Automation
- **Pattern recognition** for repetitive tasks
- **Automation suggestions** with time-saving estimates
- **Tool recommendations** for specific automation scenarios
- **Workflow optimization** based on task frequency analysis

## 🛠 Installation
### Prerequisites
- Python 3.8 or higher
- pip package manager

### Required Dependencies
```bash
pip install numpy
```

### Setup
1. Clone or download the `personal_productivity.py` file
2. Ensure you have Python 3.8+ installed
3. Install numpy: `pip install numpy`
4. Run the script: `python personal_productivity.py`

## 💡 Usage
### Basic Usage

```python
from personal_productivity import ProductivityOptimizer, Priority
import datetime

# Initialize the optimizer with a unique user ID
optimizer = ProductivityOptimizer("your_user_id")

# Add tasks
task = optimizer.add_task(
    title="Complete project proposal",
    description="Write and review the Q2 project proposal",
    priority=Priority.HIGH,
    deadline=datetime.datetime.now() + datetime.timedelta(days=2),
    estimated_hours=4.0,
    energy_level_required=8,
    tags=["writing", "project", "deadline"]
)

# Get daily recommendations
recommendations = optimizer.get_daily_recommendations()
print(recommendations)
```

### Advanced Features
#### Task Management
```python
# Add different types of tasks
optimizer.add_task("Review emails", "Daily email processing", 
                  Priority.MEDIUM, tags=["email", "communication"])

# Complete tasks
optimizer.complete_task("task_1", actual_hours=3.5)
```

#### Productivity Session Logging
```python
# Log your work sessions for pattern analysis
optimizer.log_productivity_session(
    start_time=datetime.datetime.now() - datetime.timedelta(hours=2),
    end_time=datetime.datetime.now(),
    tasks_completed=["task_1", "task_2"],
    focus_score=8,  # 1-10 scale
    energy_level=7,  # 1-10 scale
    distractions_count=3,
    tools_used=["email", "calendar", "notion"]
)
```

## 📊 Core Components
### 1. TaskPrioritizationAgent
- **Scoring Algorithm**: Multi-factor calculation including deadline urgency (0-40 points), priority level (0-25 points), energy alignment (0-20 points), and effort vs. available time (0-15 points)
- **Dynamic Prioritization**: Adapts to current time and energy levels
- **Smart Filtering**: Only considers pending tasks for prioritization

### 2. FocusDistractionsAgent
- **Pattern Learning**: Tracks focus scores by time of day
- **Optimal Timing**: Identifies your best 2-hour focus windows
- **Distraction Analysis**: Monitors high-distraction periods
- **Personalized Tips**: Provides context-aware focus improvement suggestions

### 3. ResourceRecommendationAgent
- **Tag-Based Matching**: Recommends tools based on task categories
- **Skill Tracking**: Monitors interests for learning recommendations
- **Resource Database**: Comprehensive catalog of productivity tools and techniques
- **Duplicate Prevention**: Ensures unique, relevant recommendations

### 4. WorkflowAutomationAgent
- **Pattern Recognition**: Identifies repetitive task patterns
- **Automation Suggestions**: Provides specific automation strategies
- **Time Savings**: Calculates potential time savings for each suggestion
- **Tool Integration**: Recommends appropriate automation tools

## 🎛 Configuration
### Priority Levels
- `Priority.LOW` - Non-urgent, low-impact tasks
- `Priority.MEDIUM` - Standard tasks with moderate importance
- `Priority.HIGH` - Important tasks requiring attention
- `Priority.URGENT` - Critical tasks needing immediate action

### Task Status Options
- `TaskStatus.PENDING` - Not yet started
- `TaskStatus.IN_PROGRESS` - Currently being worked on
- `TaskStatus.COMPLETED` - Finished successfully
- `TaskStatus.CANCELLED` - Cancelled or no longer needed

### Energy Levels
Tasks and sessions use a 1-10 scale where:
- 1-3: Low energy (suitable for routine tasks)
- 4-6: Medium energy (standard work tasks)
- 7-8: High energy (creative or challenging work)
- 9-10: Peak energy (most demanding tasks)

## 📁 Data Management
### Automatic Persistence
- User data is automatically saved to `user_data/{user_id}.json`
- Data includes tasks, agent states, and productivity history
- Automatic loading on initialization

### Data Structure
```json
{
  "tasks": [...],
  "task_agent": {...},
  "focus_agent": {...},
  "resource_agent": {...},
  "automation_agent": {...},
  "current_energy": 7
}
```

## 🏷 Task Tag
- The system recognizes and provides specialized recommendations for these task categories:
**Core Categories:**
- `writing` - Content creation, documentation
- `project` - Project management, planning
- `email` - Email processing, communication
- `meeting` - Meeting preparation, attendance
- `deadline` - Time-sensitive tasks
- `communication` - Team collaboration, calls
- `preparation` - Planning, research tasks

**Tool Recommendations by Tag:**
- **Writing**: Grammarly, Hemingway Editor, Notion
- **Project**: Trello, Asana, Monday.com
- **Email**: Boomerang, Mixmax, Gmail filters
- **Meeting**: Calendly, Zoom, Otter.ai

## 🔧 Customization
### Adding New Resource Categories
```python
# Extend the resource database
optimizer.resource_agent.resource_database["custom_category"] = [
    {"name": "Custom Tool", "type": "tool", "description": "Your tool description"}
]
```

### Modifying Scoring Algorithm
- The task scoring algorithm can be customized by modifying the `calculate_task_score` method in `TaskPrioritizationAgent`.

## 📈 Analytics & Insights
### Daily Recommendations Include:
1. **Top 5 Prioritized Tasks** - Dynamically ranked based on current context
2. **Focus Recommendations** - Optimal work times and break suggestions
3. **Resource Suggestions** - Tools and techniques for current tasks
4. **Automation Opportunities** - Workflow optimization suggestions

### Productivity Metrics:
- Focus score trends by time of day
- Task completion patterns
- Energy level optimization
- Distraction frequency analysis

## 🚨 Troubleshooting
### Common Issues:
**Missing numpy dependency:**
```bash
pip install numpy
```

**JSON serialization errors:**
- Usually caused by datetime objects; the system handles this automatically

**No recommendations appearing:**
- Ensure tasks have been added and tagged appropriately
- Log productivity sessions to build pattern data

## 🔮 Future Enhancements
- **Machine Learning Integration**: Advanced pattern recognition using scikit-learn
- **Calendar Integration**: Sync with Google Calendar/Outlook
- **Mobile App**: React Native or Flutter mobile interface
- **Team Collaboration**: Multi-user productivity optimization
- **Advanced Analytics**: Detailed productivity reporting and insights
- **Natural Language Processing**: Better task categorization using NLP
- **Integration APIs**: Connect with popular productivity tools

## 📄 License
- This project is provided as-is for educational and personal use. Feel free to modify and extend according to your needs.

## 🤝 Contributing
- This is a personal productivity system, but contributions and suggestions are welcome! Key areas for improvement:
- Enhanced pattern recognition algorithms
- Additional resource categories and tools
- Better automation suggestion logic
- User interface development
- Performance optimizations

## 📞 Support
- For questions or issues, please review the code comments and documentation. The system is designed to be self-explanatory and extensible.
- **Happy Productivity! 🎯**
---
