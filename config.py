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
        "introduction", "motivation", "background", "related work", "literature review", "appendix",
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
        You are an expert research assistant specializing in extracting raw factual information from computer science and software engineering research papers.

        Based on the following research paper excerpt, extract comprehensive RAW INFORMATION about coding tasks given to participants. Focus on factual extraction without interpretation - provide all technical details exactly as mentioned.

        **RAW INFORMATION EXTRACTION:**
        Extract the following information systematically. Include EVERY detail mentioned, no matter how minor:

        1. **Task Description (Raw Details)**: Extract exactly what participants were asked to do:
            - Exact task wording from the paper
            - Specific deliverables mentioned (functions, classes, applications, fixes)
            - Input/output requirements as stated
            - Functional requirements and constraints
            - Algorithms, approaches, or methodologies specified
            - Success criteria or completion requirements
            - Task duration and time limits

        2. **Participant Information (Exact Details)**: Extract all participant information:
            - Exact skill level descriptions ("graduate students", "professional developers", "novices")
            - Background details ("CS majors", "bootcamp graduates", "industry professionals")
            - Experience levels if mentioned (years, projects, etc.)
            - Specific expertise areas mentioned
            - Sample size numbers and demographics
            - Recruitment methods or criteria

        3. **Technical Details (Verbatim)**: Extract ALL technical information mentioned:
            - Programming languages explicitly mentioned
            - Library names, framework names, API names (pandas, React, Spring, etc.)
            - File extensions mentioned (.py, .js, .java, .cpp, etc.)
            - Import statements or code snippets shown
            - Tool names (VS Code, Eclipse, IntelliJ, Xcode, etc.)
            - Platform names (GitHub, AWS, Docker, etc.)
            - Version numbers or software configurations
            - Command-line tools or build systems mentioned

        4. **Context Clues (Direct Quotes)**: Extract domain and application context:
            - Application types mentioned ("web app", "mobile app", "data analysis tool")
            - Industry context ("e-commerce", "healthcare", "gaming")
            - Use case descriptions
            - Domain-specific terminology used
            - Problem domains described
            - Technology stacks mentioned

        5. **Activity Details (Specific Actions)**: Extract task activities mentioned:
            - Specific verbs used ("debug", "implement", "refactor", "analyze")
            - Types of bugs or errors mentioned
            - Implementation requirements
            - Code analysis tasks described
            - Testing or validation activities
            - Collaboration activities mentioned

        6. **Scale and Scope Indicators**: Extract size/complexity mentions:
            - Lines of code numbers
            - File counts or project sizes mentioned
            - Complexity descriptions ("simple", "enterprise-level", "prototype")
            - Existing codebase vs. from-scratch indicators
            - Project scope descriptions

        7. **Study Environment (Factual Details)**: Extract study setup information:
            - Location details (lab, remote, field)
            - Duration specifics (hours, days, sessions)
            - Individual vs. group work specifications
            - Environmental constraints mentioned
            - Special conditions or treatments

        8. **Measurement Details (Exact Metrics)**: Extract evaluation information:
            - Specific metrics mentioned (time, accuracy, completion rate)
            - Measurement tools used
            - Data collection methods described
            - Success criteria specified
            - Assessment approaches mentioned

        9. **Tool and Environment Specifics**: Extract development environment details:
            - IDE names specifically mentioned
            - Development environment descriptions
            - Debugging tool names
            - Testing framework names
            - Custom tool descriptions
            - Platform specifications

        10. **Research Context (Direct Information)**: Extract research focus details:
            - Research questions quoted
            - Hypotheses mentioned
            - Behavioral aspects being studied
            - Learning objectives stated
            - User experience factors mentioned

        **CRITICAL EXTRACTION RULES:**
        - Quote exact technical terms, tool names, and version numbers
        - Include ALL numbers, percentages, and quantitative details
        - Extract implicit clues (e.g., "npm install" implies JavaScript/Node.js)
        - Note file extensions, import statements, syntax examples
        - Include negative information ("no debugging tools provided")
        - Capture uncertainty markers ("likely", "possibly", "appeared to")
        - Extract domain-specific jargon and terminology
        - Include participant quotes about their experience or background

        **OUTPUT FORMAT:**
        Provide a comprehensive, fact-dense paragraph containing ALL extracted information. Start with task details, then systematically include all participant information, technical specifics, environmental details, and research context. Use exact quotes where available and include all technical indicators found.

        **TECHNICAL INDICATOR FOCUS:**
        Pay special attention to:
        - Library/framework names (pandas, React, Spring, Unity, etc.)
        - File extensions (.py, .js, .java, .html, .css, etc.)
        - Tool names (VS Code, Eclipse, Xcode, Git, Docker, etc.)
        - Code syntax or language-specific terms
        - Platform names (GitHub, AWS, Android Studio, etc.)
        - Version control indicators
        - Build system mentions (npm, gradle, make, etc.)

        If no user study with a coding task is described in the text, respond with exactly: "Not found"
    """

    def __init__(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SECTIONED_PAPER_DIR,
            self.SPLIT_TEXT_DIR, self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]

        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)
