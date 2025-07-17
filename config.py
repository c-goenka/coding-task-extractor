from pathlib import Path

class Config:
    DATA_DIR = Path('data')
    PARSED_PAPER_DIR = DATA_DIR / 'parsed'
    SECTIONED_PAPER_DIR = DATA_DIR / 'sectioned'
    SPLIT_TEXT_DIR = DATA_DIR / 'split'
    VECTOR_STORE_DIR = DATA_DIR / 'vector_stores'
    RESULT_DIR = DATA_DIR / 'results'

    FILTER_KEYWORDS = [
        # Core study terms
        'user', 'study', 'participant', 'subject', 'volunteer',
        'experiment', 'trial', 'test', 'eval', 'evaluation', 'assess',

        # Human subjects and participants
        'human', 'people', 'person', 'individual', 'recruit', 'recruited',
        'developer', 'programmer', 'coder', 'student', 'professional',

        # Study types and methodologies
        'empirical', 'qualitative', 'quantitative', 'survey', 'interview',
        'observation', 'case study', 'field study', 'lab study',
        'controlled study', 'randomized', 'within-subject', 'between-subject',

        # Task-related terms
        'task', 'assignment', 'exercise', 'problem', 'challenge',
        'implementation', 'coding', 'programming', 'development',
        'debug', 'refactor', 'review', 'write code', 'software',

        # Research methods
        'methodology', 'protocol', 'procedure', 'design', 'analysis',
        'data collection', 'measurement', 'metric', 'performance',
        'usability', 'user experience', 'effectiveness', 'efficiency',

        # Study conditions and comparisons
        'condition', 'treatment', 'control', 'baseline', 'comparison',
        'group', 'cohort', 'sample', 'population',

        # Common study verbs
        'conducted', 'performed', 'administered', 'collected', 'measured',
        'observed', 'recorded', 'analyzed', 'compared', 'investigated',

        # Tools and environments
        'IDE', 'editor', 'environment', 'tool', 'platform', 'system',
        'interface', 'workspace',

        # Results and findings
        'result', 'finding', 'outcome', 'effect', 'impact', 'influence',
        'correlation', 'significant', 'evidence'
    ]

    SECTION_NAMES = [
        "abstract", "introduction", "intro", "motivation", "background", "problem statement",
        "related work", "literature review", "method", "methodology", "study", "user study",
        "study design", "experimental setup", "participants", "procedure", "tasks", "task design",
        "materials", "apparatus", "implementation", "system", "system design", "system overview",
        "design goals", "evaluation", "user testing", "results", "findings", "analysis",
        "discussion", "limitations", "future work", "conclusion", "summary", "references",
        "acknowledgments", "bibliography", "appendix"
    ]

    SKIP_SECTIONS = [
        "introduction", "motivation", "background", "related work", "literature review", "appendix"
        "problem statement", "future work", "references", "acknowledgments", "bibliography"
    ]

    FUZZY_MATCH_THRESHOLD = 50
    LARGE_SECTION_THRESHOLD = 2000  # Keep sections larger than this even if in skip list
    KEYWORD_DENSITY_THRESHOLD = 0.02  # Keep sections with >2% keyword density

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    EMBEDDING_MODEL = 'text-embedding-3-small'

    LLM_MODEL = 'gpt-4o-mini'
    LLM_TEMPERATURE = 0.2
    SYSTEM_PROMPT="""
        You are an expert research assistant specializing in analyzing computer science and software engineering research papers.

        Based on the following research paper excerpt, extract comprehensive information about the coding task given to participants in any user study. Your response should capture ALL available details to support downstream task categorization.

        **EXTRACTION REQUIREMENTS:**
        Extract the following information systematically. Include all available details, even if they seem minor:

        1. **Task Description**: What exactly were participants asked to code or implement? Include:
            - Specific deliverables (functions, classes, applications, fixes)
            - Input/output requirements
            - Functional requirements and constraints
            - Any specific algorithms or approaches required
            - Success criteria or completion requirements

        2. **Participant Details**: Extract all information about study participants:
            - Skill level (expert/intermediate/beginner) with supporting evidence
            - Background (students, professionals, bootcamp graduates)
            - Years of experience if mentioned
            - Specific expertise areas (e.g., "React developers," "ML engineers")
            - Sample size and demographic information

        3. **Technical Context**: Extract all technical details:
            - Programming language(s) used (look for code snippets, imports, syntax)
            - Specific libraries, frameworks, or APIs mentioned
            - Development tools, IDEs, or platforms used
            - Version control systems or collaboration tools
            - Any specific software versions or configurations

        4. **Programming Domain and Sub-Domain**: Identify:
            - Primary programming domain (web dev, data science, mobile, etc.)
            - Specific sub-domains (e.g., "machine learning classification" within data science)
            - Application context (e.g., "e-commerce platform," "scientific simulation")
            - Industry or use case context

        5. **Task Type and Activity Details**: Identify:
            - Primary activity (debugging, implementation, code reading, etc.)
            - Secondary activities if multiple tasks were involved
            - Specific debugging types (syntax errors, logic bugs, performance issues)
            - Implementation types (new features, API integration, UI components)
            - Code comprehension tasks (tracing, explanation, documentation)

        6. **Code Size and Scope**: Extract information about:
            - Size of codebase worked with (lines of code, number of files)
            - Scope descriptions (snippet, function, module, full application)
            - Complexity indicators (simple script vs. enterprise application)
            - Pre-existing code vs. from-scratch development

        7. **Study Design and Environment**: Extract:
            - Study duration and time constraints
            - Lab vs. remote vs. field study setting
            - Individual vs. collaborative work
            - Controlled vs. naturalistic environment
            - Any special conditions or treatments

        8. **Evaluation and Metrics**: Extract information about:
            - How task success was measured (completion rate, correctness, time)
            - Performance metrics collected (errors, efficiency, quality scores)
            - Evaluation criteria or rubrics used
            - Data collection methods (logging, observation, interviews)
            - Any automated assessment tools used

        9. **Tools and Environment**: Extract details about:
            - Specific IDEs or editors used (VS Code, Eclipse, etc.)
            - Development environments (local, cloud, containers)
            - Debugging tools or profilers
            - Testing frameworks or quality tools
            - Any custom tools or plugins developed for the study

        10. **Research Focus**: Extract information about:
            - What specific aspect of coding behavior was being studied
            - Research questions or hypotheses being tested
            - Cognitive processes being investigated (attention, memory, problem-solving)
            - Usability or user experience aspects
            - Learning outcomes or skill development goals

        **OUTPUT FORMAT:**
        Structure your response as a comprehensive paragraph that naturally incorporates ALL extracted information. Start with the task description, then systematically include participant details, technical context, study design, evaluation methods, and research focus. Be thorough and include all available details.

        **CRITICAL INSTRUCTIONS:**
        - Extract information even if it seems indirect or implicit
        - Look for technical details in methodology, results, and discussion sections
        - Include quantitative details (numbers, percentages, time durations)
        - Capture tool names, version numbers, and specific configurations
        - Note any limitations or constraints mentioned
        - Include information about what was NOT allowed or available

        **Edge Case Handling:**
        - If multiple programming languages: list primary first, then others
        - If multiple domains: choose most prominent, mention others in context
        - If unclear details: indicate uncertainty level ("likely," "possibly," "unclear")
        - If information is missing: explicitly state "Not specified" for that aspect
        - If multiple studies: focus on the most relevant or detailed one

        If no user study with a coding task is described in the text, respond with exactly: "Not found"

        **Example of comprehensive response:**
        "In the study, participants were asked to implement a real-time collaborative code editor with syntax highlighting, auto-completion, and conflict resolution features, requiring them to build both frontend UI components and backend WebSocket handling for synchronization. The task involved creating a working prototype that could handle multiple simultaneous users editing the same document with live cursor tracking and change propagation. The participants were intermediate programmers consisting of 24 computer science graduate students with 2-4 years of JavaScript experience and prior exposure to React development. The implementation used JavaScript with React for the frontend and Node.js with Socket.io for real-time communication, confirmed by code snippets showing JSX syntax and WebSocket event handlers in the study materials. This coding task falls within the Web Development domain, specifically in the Real-time Applications sub-domain, and is classified as Implementation/Feature Development based on the primary goal of creating new collaborative functionality from scratch. The study took place over 3 hours in a controlled lab setting using VS Code with live-share extensions, participants worked in pairs using pair programming methodology, and success was measured through functional completeness (70%), code quality metrics using ESLint (20%), and user experience ratings from peer testing (10%). The research focused on understanding how developers coordinate work and resolve conflicts in real-time collaborative environments, with particular attention to communication patterns and decision-making processes during concurrent editing sessions."
    """

    def __init__(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SECTIONED_PAPER_DIR,
            self.SPLIT_TEXT_DIR, self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]

        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)
