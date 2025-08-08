"""Prompts for the simplified pipeline stages."""

from .binary_classification import BinaryClassificationPrompt
from .task_extraction import TaskExtractionPrompt
from .categorization import CategorizationPrompt

__all__ = ["BinaryClassificationPrompt", "TaskExtractionPrompt", "CategorizationPrompt"]