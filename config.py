from pathlib import Path

class Config:
    DATA_DIR = Path('data')
    PARSED_PAPER_DIR = DATA_DIR / 'parsed'
    SECTIONED_PAPER_DIR = DATA_DIR / 'sectioned'
    SPLIT_TEXT_DIR = DATA_DIR / 'split'
    VECTOR_STORE_DIR = DATA_DIR / 'vector_stores'
    RESULT_DIR = DATA_DIR / 'results'

    FILTER_KEYWORDS = [
        'user', 'study', 'participant', 'subject',
        'eval', 'experiment', 'trial', 'test'
    ]

    LIKELY_TASK_SECTIONS = [
        'method', 'procedure', 'study', 'task', 'evaluation', 'experiment',
        'result', 'findings', 'design', 'goal', 'finding', 'participant'
    ]

    FUZZY_MATCH_THRESHOLD = 60

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    EMBEDDING_MODEL = 'text-embedding-3-small'

    LLM_MODEL = 'gpt-4o-mini'
    LLM_TEMPERATURE = 0.2
    SYSTEM_PROMPT="""
        You are an expert research assistant specializing in analyzing computer science and software engineering research papers.

        Based on the following research paper excerpt, extract information about the coding task given to participants in any user study. Your response should be concise and cover these aspects:

        1. **Task Description**: What exactly were participants asked to code or implement? Be specific about the requirements, goals, and constraints.

        2. **Programming Language**: What programming language(s) were used? If not explicitly stated, make an educated guess based on context clues (libraries, frameworks, syntax examples, etc.).

        3. **Task Category**: Classify the coding task into one of these categories:
           - Data Science/Analytics (data analysis, visualization, machine learning, statistics)
           - Web Development (frontend, backend, full-stack, web APIs)
           - Algorithmic/Problem Solving (algorithms, data structures, competitive programming)
           - System Programming (operating systems, networking, low-level programming)
           - Mobile Development (iOS, Android, cross-platform)
           - Game Development
           - Software Engineering (debugging, refactoring, testing, code review)
           - Other (specify what type)

        4. **Additional Context**: Include any relevant details about the study setup, tools used, time constraints, or special conditions.

        Structure your response as a flowing paragraph that naturally incorporates all this information. Start with the task description, then mention the programming language, followed by the task category, and end with any additional context.

        If no user study with a coding task is described in the text, respond with exactly: "Not found"

        Examples of good responses:
        - "Participants were asked to implement a sorting algorithm that could handle large datasets efficiently within a 2-hour time limit. The task was completed in Java and falls under the algorithmic/problem solving category. The study was conducted in a controlled lab environment with participants using Eclipse IDE and having access to standard Java documentation."

        - "The coding task involved building a web application for managing student records with user authentication and data visualization features. Participants used JavaScript with React framework for the frontend and Node.js for the backend, making this a web development task. The study allowed 4 hours for completion and participants could use any code editor of their choice."
    """

    def __init__(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SECTIONED_PAPER_DIR,
            self.SPLIT_TEXT_DIR, self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]

        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)
