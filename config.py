"""Configuration settings for the simplified pipeline."""

from typing import Dict, List


class Config:
    """Configuration class for the simplified pipeline."""

    # LLM Settings
    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0.2

    # Filtering Thresholds
    FILTER_THRESHOLD_LOW = 0.3    # Below this: skip paper entirely
    FILTER_THRESHOLD_HIGH = 0.6   # Above this: auto-accept as programming

    # Quality Control Thresholds
    QUALITY_THRESHOLD_RETRY = 0.3     # Below this: retry extraction
    QUALITY_THRESHOLD_REVIEW = 0.6    # Below this: flag for manual review

    # Processing Settings
    RATE_LIMIT_DELAY = 0.5  # Seconds between API calls
    MAX_RETRIES = 2         # Maximum retries for failed extractions

    # Output Settings
    SAVE_INTERMEDIATE_RESULTS = True
    INCLUDE_RAW_RESPONSES = True

    @classmethod
    def get_default_settings(cls) -> Dict:
        """Get default pipeline settings."""
        return {
            'model': cls.DEFAULT_MODEL,
            'temperature': cls.DEFAULT_TEMPERATURE,
            'filter_threshold_low': cls.FILTER_THRESHOLD_LOW,
            'filter_threshold_high': cls.FILTER_THRESHOLD_HIGH,
        }

    @classmethod
    def get_quality_thresholds(cls) -> Dict[str, float]:
        """Get quality control thresholds."""
        return {
            'retry': cls.QUALITY_THRESHOLD_RETRY,
            'review': cls.QUALITY_THRESHOLD_REVIEW,
        }
