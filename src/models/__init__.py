"""Data models for the simplified pipeline."""

from .task_models import (
    Paper,
    FilterResult,
    TaskExtractionResult,
    TaskCategories,
    QualityScore,
    PipelineResult
)

__all__ = [
    "Paper",
    "FilterResult",
    "TaskExtractionResult",
    "TaskCategories",
    "QualityScore",
    "PipelineResult"
]
