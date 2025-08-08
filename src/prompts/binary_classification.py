"""
Stage 1: Binary Classification Prompt

This prompt determines whether a research paper describes a user study involving
coding/programming tasks. It's designed to be short, focused, and accurate.
"""

class BinaryClassificationPrompt:
    """Generates prompts for binary programming study classification."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for binary classification."""
        return """You are an expert research assistant specializing in identifying programming and coding user studies in HCI research papers.

Your task is to determine: Does this paper describe a user study where participants performed coding, programming, or software development tasks?

RESPOND WITH EXACTLY THIS FORMAT:
Decision: [YES or NO]
Confidence: [0.0-1.0]
Reason: [One sentence explanation]

WHAT COUNTS AS YES (Programming User Study):
- Participants wrote, edited, or debugged code
- Participants used programming tools (IDEs, debuggers, code editors)
- Participants implemented algorithms or software features
- Participants used AI coding assistants (Copilot, ChatGPT for code)
- Participants worked with visual programming languages (Scratch, Blockly)
- Participants performed code review or analysis tasks

WHAT COUNTS AS NO (Not Programming Study):
- Papers that only MENTION programming but don't study it
- System papers describing tools without user evaluation
- Survey/review papers analyzing other research
- Studies of general software usage (using apps, not building them)
- UI/UX studies without programming components
- Purely theoretical or algorithmic papers

EXAMPLES:

Paper: "We conducted a study where 20 developers used VS Code to debug Python applications. Participants were given buggy code and asked to identify and fix errors."
Decision: YES
Confidence: 0.95
Reason: Participants actively debugged code using programming tools.

Paper: "Our system automatically generates UI layouts using machine learning. We evaluated the quality of generated interfaces through expert review."
Decision: NO
Confidence: 0.9
Reason: Expert review of generated outputs, no programming tasks performed by participants.

Paper: "We surveyed 100 software developers about their experiences with pair programming and collaborative coding practices."
Decision: NO
Confidence: 0.9
Reason: Survey research about programming practices, no hands-on coding tasks.

Be decisive but honest about your confidence level."""

    @staticmethod
    def get_user_prompt_template() -> str:
        """Get the template for the user prompt."""
        return """Based on the following research paper information, determine if this describes a programming user study:

Title: {title}

{content_description}: {abstract}

{additional_context}

NOTE: {content_note}

Analyze this content and respond in the exact format specified."""

    @classmethod
    def format_prompt(cls, title: str, abstract: str, additional_context: str = "") -> dict:
        """Format the complete prompt for this paper."""
        system = cls.get_system_prompt()
        
        # Determine if we're using actual abstract or title fallback
        if abstract.startswith("Title: "):
            content_description = "Title (no abstract available)"
            content_note = "This paper lacks an abstract, so we're using only the title. Be more conservative in your assessment."
            actual_content = abstract[7:]  # Remove "Title:" prefix
        else:
            content_description = "Abstract"
            content_note = "Full abstract is available for analysis."
            actual_content = abstract
        
        user = cls.get_user_prompt_template().format(
            title=title,
            content_description=content_description,
            abstract=actual_content,
            additional_context=additional_context,
            content_note=content_note
        )
        
        return {
            "system": system,
            "user": user
        }