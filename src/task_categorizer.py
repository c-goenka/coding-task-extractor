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
    is_programming_related: Optional[str] = Field(default=None, description='is the research paper and user study task programming related')
    is_ai_related: Optional[str] = Field(default=None, description='is the research paper and user study task AI/LLM related')


class TaskCategorizer:
    def __init__(self, config):
        self.config = config
        self.llm = ChatOpenAI(model=self.config.LLM_MODEL, temperature=self.config.LLM_TEMPERATURE)
        self.llm = self.llm.with_structured_output(TaskCategories)
        self.setup_chain()

    def setup_chain(self):
        system_prompt = """
        You are an expert research assistant classifying coding tasks from user studies. Extract the following programming task properties from the provided task description extracted from a paper. IMPORTANT: Make educated guesses based on all available context rather than defaulting to "Not specified", "Mixed", or "Other".

        1. **Task Summary**: A clear and concise summary of the task description

        2. **Skill Level**: Skill level of the user study participants. Use these criteria and make educated guesses:
            - Expert: Professional developers, graduate students, 3+ years experience, researchers, industry professionals
            - Intermediate: Undergraduate CS students (upper-level), bootcamp graduates, 1-3 years experience, hobbyists with some experience
            - Beginner: Introductory CS students, new learners, <1 year experience, novices, people with no prior experience

            **Important**: If participants have varying skill levels, list them separated by commas (e.g., "Beginner, Intermediate" or "Intermediate, Expert") rather than using "Mixed"

            **Inference guidelines:**
            - If participants are "recruited from universities" or "CS students" → likely Intermediate
            - If "professional developers", "industry professionals", "full-time developers" → Expert
            - If "novices", "no experience", "introductory", "new learners" mentioned → Beginner
            - If mix of professionals and students → "Intermediate, Expert"
            - If PhD students, researchers, or "graduate students" → Expert
            - If undergraduates without CS background → Beginner
            - If "experienced users", "skilled practitioners", "3+ years" → Expert
            - If "bootcamp graduates", "hobbyists", "some experience" → Intermediate
            - If "specific experience in domain" mentioned → likely Intermediate to Expert
            - If participants have "varying skill levels" or "mixed backgrounds" → list the levels present (e.g., "Beginner, Intermediate, Expert")
            - Default to "Intermediate" if ambiguous but educational context present

        3. **Programming Language**: What programming language(s) were used? Analyze the extracted context for these indicators:
            
            **Primary Indicators (look for these first):**
            - File extensions: .py=Python, .js/.jsx/.ts/.tsx=JavaScript/TypeScript, .java=Java, .cpp/.c/.h=C/C++, .cs=C#, .swift=Swift, .kt=Kotlin, .rb=Ruby, .php=PHP, .go=Go, .rs=Rust, .html/.css=Web technologies
            - Library/framework names: pandas/numpy/matplotlib/scikit-learn/tensorflow=Python, React/Angular/Vue/Node.js/Express=JavaScript, Spring/Hibernate=Java, .NET/Entity Framework=C#, SwiftUI/UIKit=Swift, Flutter=Dart, Rails=Ruby
            - Code syntax clues: import/from statements=Python, require/import=JavaScript, import/package=Java, using=C#, #include=C/C++
            - Tool indicators: pip/conda=Python, npm/yarn/webpack=JavaScript, gradle/maven=Java, NuGet=C#, CocoaPods/Swift Package Manager=Swift, Cargo=Rust
            
            **Secondary Indicators:**
            - Platform/IDE mentions: Xcode=Swift, Android Studio=Java/Kotlin, Visual Studio=C#/.NET, PyCharm=Python, WebStorm=JavaScript
            - Domain patterns: Data science/ML=likely Python, Web development=likely JavaScript, iOS=Swift, Android=Java/Kotlin, Game development=C# (Unity) or C++, System programming=C/C++/Rust
            - Build systems: npm=JavaScript, pip=Python, gradle=Java, make=C/C++, cargo=Rust
            
            **Inference Priority:**
            1. If multiple indicators point to same language → Use that language with confidence
            2. If mixed indicators → List primary language first, then mention others
            3. If domain context only → Use format "Language (inferred from domain context)"
            4. If web-related without specifics → "JavaScript (web development context)"
            5. If data science/ML context → "Python (data science context)"
            6. If mobile development → "Swift (iOS) or Java/Kotlin (Android)"
            7. Only use "Not specified" if absolutely no technical indicators exist

        4. **Programming Domain**: Classify the coding task into one of these domains. Make educated guesses based on context:
            - Data Science/Analytics: Data manipulation, statistical analysis, machine learning, visualization, scientific computing
            - Web Development: Web applications, websites, APIs, web services (frontend, backend, full-stack)
            - Mobile Development: iOS, Android, cross-platform mobile apps
            - Game Development: Game engines, game logic, graphics, interactive entertainment
            - Human-Computer Interaction: User interfaces, interaction design, accessibility, usability tools
            - Artificial Intelligence/ML: AI models, machine learning, natural language processing, computer vision
            - System Programming: Operating systems, networking, embedded systems, low-level programming
            - Software Engineering: Development processes, code quality, maintenance, development tooling
            - Creative/Media: Graphics, animation, video processing, audio, creative tools
            - Education/Learning: Educational software, learning platforms, tutoring systems
            - Research Tools: Academic research software, data collection tools, analysis platforms

            **Domain inference guidelines:**
            - If mentions "user interface", "interaction", "usability", "AR", "VR", "augmented reality" → Human-Computer Interaction
            - If mentions "AI", "machine learning", "neural networks", "LLM", "GPT", "ChatGPT" → Artificial Intelligence/ML
            - If mentions "animation", "video", "graphics", "creative", "generative art" → Creative/Media
            - If mentions "students", "learning", "educational", "tutoring" → Education/Learning
            - If mentions "research", "academic", "study platform", "data collection" → Research Tools
            - If mentions "web", "website", "React", "Angular", "Vue", "frontend", "backend" → Web Development
            - If mentions "mobile", "iOS", "Android", "Swift", "Kotlin" specifically → Mobile Development
            - If mentions "game", "Unity", "Unreal", "gaming" → Game Development
            - If mentions "data science", "pandas", "numpy", "matplotlib", "statistical" → Data Science/Analytics
            - Default to most contextually appropriate domain, avoid "Other"

        5. **Programming Sub-Domain**: More specific sub-domain within the programming domain (e.g., "Machine Learning" within AI, "React Frontend" within Web Development, "iOS Development" within Mobile Development)

        6. **Task Type**: Classify the coding task based on the PRIMARY activity or skill being studied:
            - Debugging: Finding and fixing errors, bugs, or issues in existing code
            - Code Comprehension: Understanding, analyzing, or explaining existing code functionality
            - Feature Development: Creating new functionality or code from scratch
            - Code Quality: Improving code structure, readability, or maintainability without changing functionality
            - Testing & Validation: Writing tests, verifying correctness, or quality assurance
            - Problem Solving: Solving algorithmic challenges or computational problems
            - Tool Usage: Using development tools, IDEs, or navigating codebases
            - User Interface Design: Creating or modifying user interfaces and interactions
            - Collaboration: Working with others on code (pair programming, code review)
            - Content Creation: Creating prompts, content, or non-code artifacts using programming tools
            - Other: Make sure to specify the type if none of the above categories apply

        7. **Code Size/Scope**: Classify the size or scope of the codebase participants worked with. Analyze extracted context for these indicators:

            **Explicit Size Indicators:**
            - Lines of code mentioned: <10 lines=Snippet, 10-100 lines=Function, 100-1000 lines=Module, 1000+ lines=Full Application
            - File count mentioned: 1 file=Function/Module, 2-5 files=Module, 6+ files=Package/Library or Full Application
            - Time duration: <30 min=Snippet/Function, 30min-2hr=Function/Module, 2hr-1day=Module/Package, >1day=Full Application

            **Task Description Keywords:**
            - Snippet: "code fragment", "small script", "prompt", "single command", "one-liner", "write a function to..."
            - Function: "implement function", "write method", "create component", "single function", "algorithm implementation"
            - Module: "implement class", "create file", "build module", "single component", "standalone script"
            - Package/Library: "build library", "create framework", "multiple files", "API implementation", "plugin development"
            - Full Application: "build application", "complete system", "end-to-end implementation", "full stack", "working prototype", "deploy system"

            **Context Clues:**
            - Infrastructure mentions (databases, servers, deployment) → Full Application
            - Multiple technology mentions (frontend+backend, multiple frameworks) → Full Application
            - Testing framework setup mentioned → Module or larger
            - Single algorithm/logic task → Function
            - Quick task or tutorial → Snippet
            - Project setup mentioned (package.json, requirements.txt) → Module or larger

            **Inference Priority:**
            1. Use explicit numbers if mentioned (lines, files, duration)
            2. Match task description keywords
            3. Infer from complexity indicators and context
            4. Default to "Function" only if no other indicators available

        8. **Evaluation Metrics**: How was task success or performance measured in the study? (e.g., completion time, accuracy, code quality scores, bug detection rate, user satisfaction)

        9. **Tools/Environment**: Specific tools, IDEs, or development environments used in the study (e.g., VS Code, Eclipse, online coding platforms, specific debugging tools)

        10. **Research Focus**: What specific aspect of coding behavior or performance was being studied? (e.g., code navigation patterns, debugging strategies, collaboration effectiveness, learning outcomes)

        11. **Programming Related**: Is this research paper and user study task programming/coding related? Yes or No

        12. **AI or LLM Related**: Is this research paper and user study task AI or LLM related? Yes or No

        **General Guidelines:**
        - Always make educated guesses based on contextual clues rather than using "Not specified"
        - Carefully analyze all technical indicators provided in the raw extracted context
        - Look for exact technical terms, file extensions, library names, and tool mentions in the context
        - For skill levels: Use comma-separated values (e.g., "Beginner, Intermediate") when participants have varying skill levels instead of "Mixed"
        - Use "Other" only when the task genuinely doesn't fit existing categories AND specify what it is
        - Consider the broader context of the study, participant backgrounds, and research goals
        - If multiple programming languages are used, list the primary language first, then others
        - If task spans multiple domains, choose the most prominent one and mention others in context
        - If task involves multiple activities, classify by the activity that consumed the most time or was the main objective
        - Pay special attention to quantitative details (numbers, percentages, time durations) for scope classification
        - Use quoted technical terms and exact tool names from the context when making classifications

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
                'research_focus' : task_categories.research_focus,
                'is_programming_related': task_categories.is_programming_related,
                'is_ai_related': task_categories.is_ai_related
            }

        return results
