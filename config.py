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
        'result', 'findings', 'design', 'goal', 'finding', 'participant',
        'discussion', 'conclusion', 'limitation'
    ]

    FUZZY_MATCH_THRESHOLD = 50

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    EMBEDDING_MODEL = 'text-embedding-3-small'

    LLM_MODEL = 'gpt-4o-mini'
    LLM_TEMPERATURE = 0.2
    SYSTEM_PROMPT="""
        You are an expert research assistant specializing in analyzing computer science and software engineering research papers.

        Based on the following research paper excerpt, extract information about the coding task given to participants in any user study. Your response should be clear and cover these aspects:

        1. **Task Description**: What exactly were participants asked to code or implement? Be specific about the requirements, goals, and constraints.

        2. **Skill Level of Participants**: Were the participants expert, intermediate, or beginner programmers?

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

        5. **Task Type**: Classify the coding task based on the type of activity participants performed:
            - Debugging (Example: Fix a set of bugs in a JavaScript app)
            - Implementation (Example: Add a feature to a React component)
            - Code Reading (Example: Understand a Python function and answer questions)
            - Refactoring (Example: Clean up poorly written code)
            - Testing (Example: Write test cases for given functions)
            - Navigation/Search (Example: Locate where a variable is defined using a code browser)
            - Other (specify what type)

        6. **Additional Context**: Include any relevant details about the study setup, tools used, time constraints, or special conditions.

        Structure your response as a flowing paragraph that naturally incorporates all this information. Start with the task description, then mention the skill level and programming language, followed by the programming domain and task type, and end with any additional context.

        If no user study with a coding task is described in the text, respond with exactly: "Not found"

        Examples of good responses:
        - "In the study, participants were asked to implement a small Python script to analyze a CSV dataset containing sales records. They were required to compute summary statistics, filter entries based on given criteria, and generate a simple bar chart using the matplotlib library. The participants were beginner programmers, primarily undergraduate students enrolled in an introductory programming course. The task was completed in Python, confirmed through library mentions and code snippets. This coding task falls within the Data Science/Analytics domain and is classified as an Implementation activity. The study took place during a 1-hour lab session, and participants used Jupyter Notebooks hosted on an institutional server."

        - "Participants were asked to debug a pre-written JavaScript web application containing both syntactic and logic errors related to user interaction and data handling. They had to locate and fix issues in the front-end interface and underlying event-handling logic, aiming to restore full app functionality. The participants were intermediate-level programmers with at least two years of experience in web development. The task used JavaScript as the primary language, and contextual clues such as DOM manipulation and use of console.log confirmed this. The coding task falls under Web Development and is best categorized as a Debugging activity. The study was conducted in a controlled lab setting using a browser-based code editor, and participants had 30 minutes to complete the task. Performance was measured through correctness and completion time."
    """

    def __init__(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SECTIONED_PAPER_DIR,
            self.SPLIT_TEXT_DIR, self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]

        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)
