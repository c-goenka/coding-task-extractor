"""
Main Pipeline Orchestrator

This module orchestrates the complete simplified pipeline:
Filter → Binary Classification → Task Extraction → Categorization → Validation
"""

import time
from typing import List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.models.task_models import Paper, PipelineResult, FilterResult
from src.core.paper_filter import PaperFilter
from src.core.task_extractor import TaskExtractor
from src.core.result_validator import ResultValidator


class SimplifiedPipeline:
    """Main pipeline orchestrator for coding task extraction."""

    def __init__(self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        filter_threshold_low: float = 0.3,
        filter_threshold_high: float = 0.6):
        """
        Initialize the simplified pipeline.

        Args:
            model: LLM model to use
            temperature: LLM temperature
            filter_threshold_low: Below this score, skip paper entirely
            filter_threshold_high: Above this score, assume programming paper
        """
        self.filter = PaperFilter()
        self.extractor = TaskExtractor(model=model, temperature=temperature)
        self.validator = ResultValidator()

        self.filter_threshold_low = filter_threshold_low
        self.filter_threshold_high = filter_threshold_high

        # Statistics
        self.stats = {
            "total_papers": 0,
            "filtered_out": 0,
            "binary_classification_used": 0,
            "automatic_accepts": 0,
            "successful_extractions": 0,
            "api_calls_saved": 0
        }

    def process_paper(self, paper: Paper) -> PipelineResult:
        """Process a single paper through the complete pipeline."""
        start_time = time.time()

        try:
            # Stage 1: Paper Filtering
            filter_result = self.filter.filter_paper(paper)

            # Decision tree based on filter score
            if filter_result.relevance_score < self.filter_threshold_low:
                # Skip - very unlikely to be programming
                self.stats["filtered_out"] += 1
                self.stats["api_calls_saved"] += 3  # Saved 3 potential LLM calls

                return PipelineResult(
                    paper=paper,
                    filter_result=filter_result,
                    processing_time=time.time() - start_time
                )

            elif filter_result.relevance_score > self.filter_threshold_high:
                # Auto-accept - very likely programming paper
                self.stats["automatic_accepts"] += 1
                self.stats["api_calls_saved"] += 1  # Saved binary classification call

                # Skip binary classification, go straight to task extraction
                extraction_result = self.extractor.extract_task_details(paper)

            else:
                # Borderline - use binary classification
                self.stats["binary_classification_used"] += 1

                binary_result = self.extractor.classify_paper_binary(paper)

                if not binary_result.has_coding_task:
                    # Binary classifier says NO
                    return PipelineResult(
                        paper=paper,
                        filter_result=filter_result,
                        extraction_result=binary_result,
                        processing_time=time.time() - start_time
                    )

                # Binary classifier says YES - extract details
                extraction_result = self.extractor.extract_task_details(paper)

            # If we got here, we have a programming paper - categorize it
            if extraction_result.has_coding_task and extraction_result.raw_task_description:
                categories = self.extractor.categorize_task(extraction_result.raw_task_description)
                self.stats["successful_extractions"] += 1
            else:
                categories = None

            # Create result and validate
            result = PipelineResult(
                paper=paper,
                filter_result=filter_result,
                extraction_result=extraction_result,
                categories=categories,
                processing_time=time.time() - start_time
            )

            # Quality validation
            validated_result = self.validator.validate_result(result)

            return validated_result

        except Exception as e:
            return PipelineResult(
                paper=paper,
                filter_result=FilterResult(
                    paper_id=paper.paper_id,
                    is_relevant=False,
                    relevance_score=0.0,
                    reason="Processing error",
                    keywords_found=[]
                ),
                error_message=str(e),
                processing_time=time.time() - start_time
            )

    def process_papers(self, papers: List[Paper], show_progress: bool = True) -> List[PipelineResult]:
        """Process a list of papers through the complete pipeline."""

        self.stats["total_papers"] = len(papers)
        results = []

        for i, paper in enumerate(papers, 1):
            if show_progress and i % 10 == 0:
                print(f"Processing paper {i}/{len(papers)} ({100*i/len(papers):.1f}%)")

            result = self.process_paper(paper)
            results.append(result)

        return results

    def get_statistics(self) -> dict:
        """Get pipeline processing statistics."""
        total = self.stats["total_papers"]
        if total == 0:
            return self.stats

        # Calculate rates
        filter_rate = self.stats["filtered_out"] / total
        success_rate = self.stats["successful_extractions"] / total
        api_efficiency = self.stats["api_calls_saved"] / (total * 3)  # Max 3 calls per paper

        return {
            **self.stats,
            "filter_rate": filter_rate,
            "success_rate": success_rate,
            "api_efficiency": api_efficiency,
            "estimated_cost_savings": f"{api_efficiency * 100:.1f}%"
        }

    def print_summary(self, results: List[PipelineResult]):
        """Print a summary of pipeline results."""
        stats = self.get_statistics()
        validation_stats = self.validator.get_validation_summary(results)

        print("\n" + "="*60)
        print("SIMPLIFIED PIPELINE SUMMARY")
        print("="*60)

        print(f"📊 Processing Statistics:")
        print(f"   Total papers: {stats['total_papers']}")
        print(f"   Filtered out: {stats['filtered_out']} ({stats.get('filter_rate', 0)*100:.1f}%)")
        print(f"   Binary classifications: {stats['binary_classification_used']}")
        print(f"   Automatic accepts: {stats['automatic_accepts']}")
        print(f"   Successful extractions: {stats['successful_extractions']} ({stats.get('success_rate', 0)*100:.1f}%)")

        print(f"\n💰 Cost Efficiency:")
        print(f"   API calls saved: {stats['api_calls_saved']}")
        print(f"   Estimated cost savings: {stats.get('estimated_cost_savings', '0%')}")

        if validation_stats:
            print(f"\n📈 Quality Metrics:")
            avg_quality = validation_stats.get('average_quality', {})
            print(f"   Average confidence: {avg_quality.get('confidence', 0):.2f}")
            print(f"   Average completeness: {avg_quality.get('completeness', 0):.2f}")
            print(f"   Average consistency: {avg_quality.get('consistency', 0):.2f}")
            print(f"   Average overall quality: {avg_quality.get('overall', 0):.2f}")

            quality_dist = validation_stats.get('quality_distribution', {})
            print(f"\n🎯 Quality Distribution:")
            print(f"   High quality (>0.7): {quality_dist.get('high_quality', 0)}")
            print(f"   Medium quality (0.4-0.7): {quality_dist.get('medium_quality', 0)}")
            print(f"   Low quality (<0.4): {quality_dist.get('low_quality', 0)}")


# Convenience function for easy pipeline usage
def run_pipeline(papers: List[Paper], **kwargs) -> List[PipelineResult]:
    """
    Convenience function to run the complete pipeline.

    Args:
        papers: List of Paper objects to process
        **kwargs: Arguments passed to SimplifiedPipeline constructor

    Returns:
        List of PipelineResult objects
    """
    pipeline = SimplifiedPipeline(**kwargs)
    results = pipeline.process_papers(papers)
    pipeline.print_summary(results)
    return results
