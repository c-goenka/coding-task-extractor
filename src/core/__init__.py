"""Core processing components for the simplified pipeline."""

from .paper_filter import PaperFilter
from .task_extractor import TaskExtractor  
from .result_validator import ResultValidator

__all__ = ["PaperFilter", "TaskExtractor", "ResultValidator"]