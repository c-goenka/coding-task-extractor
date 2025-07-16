from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from typing import Optional
from pydantic import BaseModel, Field

class TaskCategories(BaseModel):
    task_summary: str = Field(description="task description summary")
    skill_level: Optional[str] = Field(default=None, description="participant skill level")
    programming_language: Optional[str] = Field(default=None, description='programming language used in user study')
    programming_domain: Optional[str] = Field(default=None, description="programming domain of the coding task")
    task_type: Optional[str] = Field(default=None, description='type of programming activity in the coding task')


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

        2. **Skill Level**: Skill level of the user study participants. Were the participants expert, intermediate, or beginner programmers?

        3. **Programming Language**: What programming language(s) were used? If not explicitly stated, make an educated guess based on context clues (libraries, frameworks, syntax examples, etc.).

        4. **Programming Domain**: Classify the coding task into one of these domains:
            - Data Science/Analytics (data analysis, visualization, machine learning, statistics)
            - Web Development (frontend, backend, full-stack, web APIs)
            - Algorithmic/Problem Solving (algorithms, data structures, competitive programming)
            - System Programming (operating systems, networking, low-level programming)
            - Mobile Development (iOS, Android, cross-platform)
            - Game Development
            - Software Engineering (debugging, refactoring, testing, code review)
            - Other (specify what field)

        5. **Task Type**: Classify the coding task based on the PRIMARY activity or skill being studied:
            - Debugging (Example: Identify and fix bugs, error diagnosis, troubleshooting existing code)
            - Code Comprehension (Example: Read code to understand functionality, trace execution, explain behavior)
            - Feature Development (Example: Add new functionality, implement new requirements from scratch)
            - Code Quality (Example: Refactoring, code review, improving maintainability, style fixes)
            - Testing & Validation (Example: Write tests, verify correctness, quality assurance)
            - Problem Solving (Example: Algorithmic challenges, data structure implementation, computational thinking)
            - Tool Usage (Example: IDE navigation, version control, debugging tools, code search)
            - Collaboration (Example: Code review, pair programming, discussing code with others)
            - Other (specify what type)

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
                'skill_level' : task_categories.skill_level,
                'programming_language' : task_categories.programming_language,
                'programming_domain' : task_categories.programming_domain,
                'task_type' : task_categories.task_type
            }

        return results
