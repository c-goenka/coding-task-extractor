from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from typing import Optional
from pydantic import BaseModel, Field

class TaskCategories(BaseModel):
    task_summary: str = Field(description="task description summary")
    participant_skill_level: Optional[str] = Field(default=None, description="participant skill level")
    programming_language: Optional[str] = Field(default=None, description='programming language used in user study')
    programming_domain: Optional[str] = Field(default=None, description="programming domain of the coding task")
    programming_sub_domain: Optional[str] = Field(default=None, description="more specific sub-domain within the programming domain")
    task_type: Optional[str] = Field(default=None, description='type of programming activity in the coding task')
    code_size_scope: Optional[str] = Field(default=None, description='size or scope of the codebase (small snippet, function, module, full application)')
    evaluation_metrics: Optional[str] = Field(default=None, description='how task success or performance was measured')
    tools_environment: Optional[str] = Field(default=None, description='specific tools, IDEs, or development environment used')
    research_focus: Optional[str] = Field(default=None, description='what specific aspect of coding behavior or performance was being studied')


class TaskCategorizer:
    def __init__(self, config):
        self.config = config
        self.llm = ChatOpenAI(model=self.config.LLM_MODEL, temperature=self.config.LLM_TEMPERATURE)
        self.llm = self.llm.with_structured_output(TaskCategories)
        self.setup_chain()

    def setup_chain(self):
        system_prompt = """
        You are an expert research assistant classifying coding tasks from user studies. Extract the following programming task properties from the provided task description extracted from a paper:

        1. **Task Summary**: A clear and concise summary of the task description

        2. **Skill Level**: Skill level of the user study participants. Use these criteria:
            - Expert: Professional developers, graduate students, or those with 3+ years experience
            - Intermediate: Undergraduate CS students (upper-level), bootcamp graduates, or 1-3 years experience
            - Beginner: Introductory CS students, new learners, or less than 1 year experience
            - If unclear or mixed skill levels, respond with "Not specified" or "Mixed"

        3. **Programming Language**: What programming language(s) were used? If not explicitly stated, classify based on:
            - Code snippets or syntax examples shown
            - Specific libraries/frameworks mentioned (e.g., React=JavaScript, pandas=Python, SwiftUI=Swift)
            - Development tools mentioned (e.g., Xcode=Swift, Visual Studio=C#, npm=JavaScript)
            - If uncertain, indicate confidence level (e.g., "Python (likely based on matplotlib mention)" or "Not specified")

        4. **Programming Domain**: Classify the coding task into one of these domains (choose the most prominent one):
            - Data Science/Analytics: Tasks involving data manipulation, statistical analysis, machine learning, visualization, or scientific computing
            - Web Development: Tasks focused on web applications, websites, APIs, or web services (frontend, backend, or full-stack)
            - Algorithmic/Problem Solving: Tasks primarily about implementing algorithms, data structures, or solving computational problems
            - System Programming: Tasks involving operating systems, networking, embedded systems, or low-level programming
            - Mobile Development: Tasks specifically for mobile platforms (iOS, Android, cross-platform mobile apps)
            - Game Development: Tasks involving game engines, game logic, graphics, or interactive entertainment
            - Software Engineering: Tasks focused on software development processes, code quality, maintenance, or development tooling (NOT domain-specific implementation)
            - Other: Specify the field if none of the above domains apply

        5. **Programming Sub-Domain**: More specific sub-domain within the programming domain (e.g., "Machine Learning" within Data Science, "React Frontend" within Web Development, "Graph Algorithms" within Algorithmic/Problem Solving)

        6. **Task Type**: Classify the coding task based on the PRIMARY activity or skill being studied (use this priority order if multiple activities are present):
            - Debugging: Primary goal is finding and fixing errors, bugs, or issues in existing code
            - Code Comprehension: Primary goal is understanding, analyzing, or explaining existing code functionality
            - Feature Development: Primary goal is creating new functionality or code from scratch
            - Code Quality: Primary goal is improving code structure, readability, or maintainability without changing functionality
            - Testing & Validation: Primary goal is writing tests, verifying correctness, or quality assurance
            - Problem Solving: Primary goal is solving algorithmic challenges or computational problems
            - Tool Usage: Primary goal is using development tools, IDEs, or navigating codebases
            - Collaboration: Primary goal is working with others on code (pair programming, code review)
            - Other: Specify the type if none of the above categories apply

        7. **Code Size/Scope**: Classify the size or scope of the codebase participants worked with:
            - Snippet (small code fragments, few lines)
            - Function (single functions or methods)
            - Module (single files or classes)
            - Package/Library (multiple related files)
            - Full Application (complete software systems)
            - Other (specify scope)

        8. **Evaluation Metrics**: How was task success or performance measured in the study? (e.g., completion time, accuracy, code quality scores, bug detection rate, user satisfaction)

        9. **Tools/Environment**: Specific tools, IDEs, or development environments used in the study (e.g., VS Code, Eclipse, online coding platforms, specific debugging tools)

        10. **Research Focus**: What specific aspect of coding behavior or performance was being studied? (e.g., code navigation patterns, debugging strategies, collaboration effectiveness, learning outcomes)

        **Edge Case Handling:**
        - If multiple programming languages are used, list the primary language first, then others (e.g., "Python with JavaScript frontend")
        - If task spans multiple domains, choose the most prominent one and mention others in context
        - If participant skill level is unclear, respond with "Not specified" rather than guessing
        - If task involves multiple activities, classify by the activity that consumed the most time or was the main objective
        - If evaluation metrics are not mentioned, respond with "Not specified" rather than assuming
        - If code size/scope is unclear, use context clues like "small script" → Snippet, "application" → Full Application

        """

        prompt = ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('human', '{context}')
        ])

        self.chain: Runnable = prompt | self.llm

    def categorize_task(self, task_description):
        response = self.chain.invoke({'context' : task_description})
        return response

    def categorize_all_tasks(self, coding_tasks):
        results = {}

        for paper_id, task_description in coding_tasks.items():
            if task_description == 'Not found':
                continue
            task_categories = self.categorize_task(task_description)
            results[paper_id] = {
                'task_summary' : task_categories.task_summary,
                'participant_skill_level' : task_categories.participant_skill_level,
                'programming_language' : task_categories.programming_language,
                'programming_domain' : task_categories.programming_domain,
                'programming_sub_domain' : task_categories.programming_sub_domain,
                'task_type' : task_categories.task_type,
                'code_size_scope' : task_categories.code_size_scope,
                'evaluation_metrics' : task_categories.evaluation_metrics,
                'tools_environment' : task_categories.tools_environment,
                'research_focus' : task_categories.research_focus
            }

        return results
