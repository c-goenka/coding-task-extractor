from pathlib import Path

class Config:
    def __init__(self, conference_name=None):
        self.conference_name = conference_name or 'untitled'
        self.DATA_DIR = Path('data') / self.conference_name

        self.PARSED_PAPER_DIR = self.DATA_DIR / 'parsed'
        self.SPLIT_TEXT_DIR = self.DATA_DIR / 'split'
        self.VECTOR_STORE_DIR = self.DATA_DIR / 'vector_stores'
        self.RESULT_DIR = self.DATA_DIR / 'results'

        self._create_directories()
        self._setup_configuration()

    def _create_directories(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SPLIT_TEXT_DIR,
            self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]
        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _setup_configuration(self):
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200

        self.EMBEDDING_MODEL = 'text-embedding-3-small'

        self.LLM_MODEL = 'gpt-4o-mini'
        self.LLM_TEMPERATURE = 0.2
        self.SYSTEM_PROMPT = """
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
        - Include participant quotes about their experience or background

        **OUTPUT FORMAT:**
        Provide a comprehensive, fact-dense paragraph containing ALL extracted information. Start with task details, then systematically include all participant information, technical specifics, environmental details, and research context. Use exact quotes where available and include all technical indicators found.

        If no user study with a coding task is described in the text, respond with exactly: "Not found"
        """
