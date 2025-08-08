"""
Data models for the simplified coding task extraction pipeline.

These Pydantic models define the structure and validation rules for all data
flowing through our pipeline. Each model represents a specific stage or output.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from enum import Enum


class Paper(BaseModel):
    """Represents a research paper with metadata."""

    paper_id: str = Field(description="Unique identifier for the paper")
    title: str = Field(description="Paper title")
    authors: str = Field(description="Comma-separated author names")
    venue: str = Field(description="Conference or journal name")
    year: int = Field(description="Publication year")
    url: Optional[str] = Field(default=None, description="Paper URL")
    abstract: Optional[str] = Field(default=None, description="Paper abstract")
    pdf_path: Optional[str] = Field(default=None, description="Path to PDF file")


class FilterResult(BaseModel):
    """Result of paper filtering stage."""

    paper_id: str
    is_relevant: bool = Field(description="Whether paper appears to contain coding tasks")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score 0-1")
    reason: str = Field(description="Brief explanation for the decision")
    keywords_found: List[str] = Field(default=[], description="Relevant keywords detected")


class TaskExtractionResult(BaseModel):
    """Result of task extraction stage (before categorization)."""

    paper_id: str
    has_coding_task: bool = Field(description="Whether a coding task was found")
    confidence: float = Field(ge=0.0, le=1.0, description="LLM confidence in extraction")
    raw_task_description: Optional[str] = Field(default=None, description="Raw extracted task description")
    extraction_reason: str = Field(description="Brief explanation of the decision")


class SkillLevel(str, Enum):
    """Participant skill levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    MIXED = "Mixed"  # For studies with participants at multiple levels


class ProgrammingDomain(str, Enum):
    """Programming domains."""
    DATA_SCIENCE = "Data Science/Analytics"
    WEB_DEVELOPMENT = "Web Development"
    MOBILE_DEVELOPMENT = "Mobile Development"
    GAME_DEVELOPMENT = "Game Development"
    HCI = "Human-Computer Interaction"
    AI_ML = "Artificial Intelligence/ML"
    SYSTEM_PROGRAMMING = "System Programming"
    SOFTWARE_ENGINEERING = "Software Engineering"
    CREATIVE_MEDIA = "Creative/Media"
    EDUCATION = "Education/Learning"
    RESEARCH_TOOLS = "Research Tools"
    OTHER = "Other"


class TaskType(str, Enum):
    """Types of programming tasks."""
    DEBUGGING = "Debugging"
    CODE_COMPREHENSION = "Code Comprehension"
    FEATURE_DEVELOPMENT = "Feature Development"
    CODE_QUALITY = "Code Quality"
    TESTING_VALIDATION = "Testing & Validation"
    PROBLEM_SOLVING = "Problem Solving"
    TOOL_USAGE = "Tool Usage"
    UI_DESIGN = "User Interface Design"
    COLLABORATION = "Collaboration"
    CONTENT_CREATION = "Content Creation"
    OTHER = "Other"


class CodeScope(str, Enum):
    """Size/scope of code participants worked with."""
    SNIPPET = "Snippet"
    FUNCTION = "Function"
    MODULE = "Module"
    PACKAGE_LIBRARY = "Package/Library"
    FULL_APPLICATION = "Full Application"


class TaskCategories(BaseModel):
    """Categorized task information."""

    task_summary: str = Field(description="Concise summary of the coding task")
    participant_skill_level: Optional[SkillLevel] = Field(default=None)
    programming_language: Optional[str] = Field(default=None, description="Primary language(s) used")
    programming_domain: Optional[ProgrammingDomain] = Field(default=None)
    programming_sub_domain: Optional[str] = Field(default=None, description="Specific area within domain")
    task_type: Optional[TaskType] = Field(default=None)
    code_size_scope: Optional[CodeScope] = Field(default=None)
    evaluation_metrics: Optional[str] = Field(default=None, description="How performance was measured")
    tools_environment: Optional[str] = Field(default=None, description="Development tools/IDEs used")
    research_focus: Optional[str] = Field(default=None, description="What aspect was being studied")
    is_programming_related: bool = Field(description="Is this about programming tools/development")
    is_ai_related: bool = Field(description="Is this AI/LLM related")


class QualityScore(BaseModel):
    """Quality assessment of extraction results."""

    confidence: float = Field(ge=0.0, le=1.0, description="LLM confidence in extraction")
    completeness: float = Field(ge=0.0, le=1.0, description="Percentage of fields populated")
    consistency: float = Field(ge=0.0, le=1.0, description="Internal consistency score")

    @computed_field
    @property
    def overall(self) -> float:
        """Calculate overall score as weighted average."""
        # Weighted average: confidence 50%, completeness 30%, consistency 20%
        return (self.confidence * 0.5 +
                self.completeness * 0.3 +
                self.consistency * 0.2)


class PipelineResult(BaseModel):
    """Complete result from the pipeline for one paper."""

    paper: Paper
    filter_result: FilterResult
    extraction_result: Optional[TaskExtractionResult] = None
    categories: Optional[TaskCategories] = None
    quality_score: Optional[QualityScore] = None
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error if processing failed")

    @property
    def success(self) -> bool:
        """Whether processing completed successfully."""
        return self.error_message is None

    @property
    def has_valid_task(self) -> bool:
        """Whether a valid coding task was found and categorized."""
        return (self.extraction_result is not None and
                self.extraction_result.has_coding_task and
                self.categories is not None)
