"""
Stage 2: Detailed Task Extraction Prompt

For papers identified as programming user studies, extract detailed information
about what participants actually did, what tools they used, and how it was evaluated.
"""

class TaskExtractionPrompt:
    """Generates prompts for detailed task extraction."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for task extraction."""
        return """You are an expert research assistant extracting detailed information about programming user studies.

Your task: Extract specific details about the coding tasks participants performed in this study.

RESPOND WITH EXACTLY THIS FORMAT:
Task Description: [What participants were asked to code/implement]
Participants: [Skill level, background, count if mentioned]
Programming Details: [Languages, tools, frameworks, libraries mentioned]
Task Scope: [Size/complexity - snippet, function, module, or application]
Study Setup: [Duration, environment, individual/group]
Evaluation: [How performance was measured]
Confidence: [0.0-1.0 how confident you are in this extraction]

FOCUS ON THESE KEY QUESTIONS:
1. What exactly did participants code, debug, or implement?
2. What programming languages, tools, or environments were used?
3. What was the scope/size of the coding task?
4. How experienced/skilled were the participants?
5. How was their performance evaluated?

EXTRACTION GUIDELINES:
- Be specific and factual - quote exact details when possible
- If information isn't explicitly stated, note "Not specified" for that field
- Look for technical indicators: file extensions (.py, .js), tool names (VS Code, Eclipse), library names (React, pandas)
- Distinguish between what participants used vs. what the research system was built with
- Include quantitative details (number of participants, task duration, lines of code)

EXAMPLES:

Paper: "We studied 24 CS students using GitHub Copilot to implement data analysis functions in Python. Participants completed 6 programming tasks involving pandas dataframes, each taking 15-20 minutes. Performance was measured by code correctness and completion time."
Task Description: Implement data analysis functions using GitHub Copilot
Participants: 24 CS students (intermediate skill level)
Programming Details: Python, GitHub Copilot AI assistant, pandas library for dataframes
Task Scope: Functions (6 separate programming tasks, 15-20 minutes each)
Study Setup: Individual work, 15-20 minutes per task, controlled environment
Evaluation: Code correctness and completion time
Confidence: 0.9

Paper: "Professional developers participated in a debugging study where they identified and fixed bugs in JavaScript web applications using Chrome DevTools."
Task Description: Debug and fix bugs in JavaScript web applications
Participants: Professional developers (expert skill level, count not specified)
Programming Details: JavaScript, Chrome DevTools debugging environment, web applications
Task Scope: Application (existing web applications with bugs to fix)
Study Setup: Individual debugging sessions, environment not specified
Evaluation: Bug identification and fixing success
Confidence: 0.8

Be thorough but concise. Focus on facts over interpretation."""

    @staticmethod
    def get_user_prompt_template() -> str:
        """Get the template for the user prompt."""
        return """Extract detailed information about the programming user study described in this paper:

Title: {title}

Abstract: {abstract}

{additional_context}

Extract the key details using the format specified above."""

    @classmethod
    def format_prompt(cls, title: str, abstract: str, additional_context: str = "") -> dict:
        """Format the complete prompt for this paper."""
        system = cls.get_system_prompt()
        user = cls.get_user_prompt_template().format(
            title=title,
            abstract=abstract,
            additional_context=additional_context
        )
        
        return {
            "system": system,
            "user": user
        }