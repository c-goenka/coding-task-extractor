"""
ResultValidator: Quality control and validation for extraction results.

This component assesses the quality of extraction results and provides
confidence scoring to help identify results that need manual review.
"""

from typing import List, Optional

from ..models.task_models import (
    Paper, FilterResult, TaskExtractionResult, 
    TaskCategories, QualityScore, PipelineResult
)


class ResultValidator:
    """Validates and scores the quality of extraction results."""
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def _calculate_completeness_score(self, categories: TaskCategories) -> float:
        """Calculate how complete the categorization is (0-1)."""
        total_fields = 0
        filled_fields = 0
        
        # Count non-None fields (excluding booleans which are always set)
        fields_to_check = [
            categories.task_summary,
            categories.participant_skill_level,
            categories.programming_language, 
            categories.programming_domain,
            categories.programming_sub_domain,
            categories.task_type,
            categories.code_size_scope,
            categories.evaluation_metrics,
            categories.tools_environment,
            categories.research_focus
        ]
        
        for field in fields_to_check:
            total_fields += 1
            if field is not None and field.strip() and field.lower() not in ['not specified', 'unknown', 'none']:
                filled_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_consistency_score(self, categories: TaskCategories) -> float:
        """Calculate internal consistency score (0-1)."""
        consistency_score = 1.0
        
        # Check domain-language consistency
        if categories.programming_language and categories.programming_domain:
            lang = categories.programming_language.lower()
            domain = categories.programming_domain.value if categories.programming_domain else ""
            
            # Common consistency checks
            consistency_checks = [
                # Data science languages should match data domain
                ("python" in lang and "pandas" in lang, "Data Science" in domain, 0.1),
                ("r " in lang or lang.startswith("r"), "Data Science" in domain, 0.1),
                
                # Web languages should match web domain  
                ("javascript" in lang or "js" in lang, "Web Development" in domain, 0.1),
                ("html" in lang or "css" in lang, "Web Development" in domain, 0.1),
                
                # Mobile languages should match mobile domain
                ("swift" in lang or "kotlin" in lang, "Mobile Development" in domain, 0.1),
                ("android" in lang or "ios" in lang, "Mobile Development" in domain, 0.1),
            ]
            
            for lang_indicator, domain_indicator, penalty in consistency_checks:
                if lang_indicator and not domain_indicator:
                    consistency_score -= penalty
                elif not lang_indicator and domain_indicator:
                    consistency_score -= penalty/2  # Less penalty for missing language
        
        # Check task type vs scope consistency
        if categories.task_type and categories.code_size_scope:
            task_type = categories.task_type.value if categories.task_type else ""
            scope = categories.code_size_scope.value if categories.code_size_scope else ""
            
            # Debugging typically doesn't create new full applications
            if "Debugging" in task_type and "Full Application" in scope:
                consistency_score -= 0.1
            
            # Feature development more likely to be larger scope
            if "Feature Development" in task_type and "Snippet" in scope:
                consistency_score -= 0.05
        
        return max(0.0, consistency_score)
    
    def calculate_quality_score(
        self, 
        extraction_result: TaskExtractionResult, 
        categories: Optional[TaskCategories]
    ) -> QualityScore:
        """Calculate overall quality score for extraction results."""
        
        # Base confidence from extraction
        confidence = extraction_result.confidence
        
        # Calculate completeness if we have categories
        if categories:
            completeness = self._calculate_completeness_score(categories)
            consistency = self._calculate_consistency_score(categories)
        else:
            completeness = 0.0
            consistency = 0.0
        
        return QualityScore(
            confidence=confidence,
            completeness=completeness, 
            consistency=consistency
        )
    
    def validate_result(self, result: PipelineResult) -> PipelineResult:
        """Validate and score a complete pipeline result."""
        
        if not result.success or not result.extraction_result:
            # Can't validate failed extractions
            return result
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(
            result.extraction_result,
            result.categories
        )
        
        # Update the result with quality score
        result.quality_score = quality_score
        
        return result
    
    def should_retry(self, quality_score: QualityScore, threshold: float = 0.3) -> bool:
        """Determine if a result should be retried due to low quality."""
        return quality_score.overall < threshold
    
    def should_flag_for_review(self, quality_score: QualityScore, threshold: float = 0.6) -> bool:
        """Determine if a result should be flagged for manual review."""
        return quality_score.overall < threshold
    
    def get_validation_summary(self, results: List[PipelineResult]) -> dict:
        """Get validation statistics for a batch of results."""
        if not results:
            return {}
        
        total = len(results)
        successful = sum(1 for r in results if r.success and r.has_valid_task)
        
        if successful == 0:
            return {
                "total_results": total,
                "successful_extractions": 0,
                "success_rate": 0.0
            }
        
        # Calculate average scores for successful extractions
        valid_results = [r for r in results if r.success and r.quality_score]
        avg_confidence = sum(r.quality_score.confidence for r in valid_results) / len(valid_results)
        avg_completeness = sum(r.quality_score.completeness for r in valid_results) / len(valid_results)  
        avg_consistency = sum(r.quality_score.consistency for r in valid_results) / len(valid_results)
        avg_overall = sum(r.quality_score.overall for r in valid_results) / len(valid_results)
        
        # Count quality levels
        high_quality = sum(1 for r in valid_results if r.quality_score.overall >= 0.7)
        medium_quality = sum(1 for r in valid_results if 0.4 <= r.quality_score.overall < 0.7)
        low_quality = sum(1 for r in valid_results if r.quality_score.overall < 0.4)
        
        return {
            "total_results": total,
            "successful_extractions": successful,
            "success_rate": successful / total,
            "average_quality": {
                "confidence": avg_confidence,
                "completeness": avg_completeness,
                "consistency": avg_consistency,
                "overall": avg_overall
            },
            "quality_distribution": {
                "high_quality": high_quality,
                "medium_quality": medium_quality, 
                "low_quality": low_quality
            }
        }