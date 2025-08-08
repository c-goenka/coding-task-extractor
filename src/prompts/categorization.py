"""
Stage 3: Task Categorization Prompt

Takes extracted task details and categorizes them into structured dimensions
using Pydantic models for reliable output.
"""

class CategorizationPrompt:
    """Generates prompts for task categorization with structured output."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for categorization."""
        return """You are an expert research assistant categorizing programming tasks from user studies.

Your task: Categorize the extracted task information into structured categories.

CATEGORIZATION GUIDELINES:

1. **Task Summary**: Write a clear, concise summary of what participants did

2. **Participant Skill Level**: 
   - Beginner: Novices, intro CS students, <1 year experience
   - Intermediate: CS students, bootcamp graduates, 1-3 years experience  
   - Expert: Professional developers, graduate students, 3+ years experience
   - Mixed: Studies with participants at multiple levels

3. **Programming Language**: Focus on what PARTICIPANTS used, not system implementation
   - Look for: file extensions (.py=Python, .js=JavaScript), library names (pandas=Python, React=JavaScript)
   - Include AI/Natural Language if participants used code generation tools
   - Multiple languages: list primary first, separated by commas

4. **Programming Domain**: Choose the most relevant domain
   - Data Science/Analytics: Data manipulation, statistical analysis, ML, visualization
   - Web Development: Web apps, APIs, frontend/backend
   - Mobile Development: iOS, Android, mobile apps
   - Human-Computer Interaction: UI tools, interaction design, accessibility
   - AI/ML: AI models, machine learning, NLP, computer vision
   - Software Engineering: Development tools, code quality, processes
   - Game Development: Games, interactive entertainment
   - Education/Learning: Educational software, learning platforms
   - Creative/Media: Graphics, animation, media processing
   - System Programming: OS, networking, low-level programming
   - Research Tools: Academic software, data collection tools
   - Other: If none fit well

5. **Task Type**: Primary activity participants performed
   - Debugging: Finding and fixing errors
   - Code Comprehension: Understanding existing code
   - Feature Development: Creating new functionality
   - Code Quality: Improving structure/readability
   - Problem Solving: Algorithmic challenges
   - Tool Usage: Using development tools/IDEs
   - Testing & Validation: Writing tests, verification
   - User Interface Design: Creating/modifying UIs
   - Collaboration: Working with others on code
   - Content Creation: Creating prompts, documentation

6. **Code Size/Scope**: Estimate based on context clues
   - Snippet: Small code fragments, single commands
   - Function: Individual functions or methods
   - Module: Single files, classes, small components
   - Package/Library: Multiple files, APIs, frameworks
   - Full Application: Complete working applications, end-to-end systems

7. **Other fields**: Extract what's mentioned, make educated guesses for the rest

INFERENCE STRATEGIES:
- "CS students" → Intermediate skill level
- "Professional developers" → Expert skill level
- "Novices" or "introductory" → Beginner skill level
- ".py files" or "pandas" → Python
- ".js" or "React" → JavaScript  
- "data analysis" → Data Science domain
- "web app" → Web Development domain
- "AI code generator" → AI/ML domain + Natural Language programming
- "debugging session" → Debugging task type
- "implement function" → Function scope

Always make educated guesses rather than leaving fields empty. Use context clues and domain knowledge."""

    @staticmethod
    def get_user_prompt_template() -> str:
        """Get the template for the user prompt."""
        return """Categorize this programming task based on the extracted details:

{task_details}

Categorize this information into the structured format specified by the TaskCategories model."""

    @classmethod
    def format_prompt(cls, task_details: str) -> dict:
        """Format the complete prompt for this task."""
        system = cls.get_system_prompt()
        user = cls.get_user_prompt_template().format(task_details=task_details)
        
        return {
            "system": system,
            "user": user
        }