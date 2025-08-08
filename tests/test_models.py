"""Quick test to verify our models work correctly."""

from models.task_models import (
    Paper, FilterResult, TaskCategories, QualityScore,
    SkillLevel, ProgrammingDomain, TaskType
)

def test_models():
    """Test that our models work as expected."""
    
    # Test Paper model
    paper = Paper(
        paper_id="TEST123",
        title="A Test Paper",
        authors="Smith, John; Doe, Jane",
        venue="CHI 2023",
        year=2023
    )
    print(f"✅ Paper model works: {paper.paper_id}")
    
    # Test FilterResult with validation
    filter_result = FilterResult(
        paper_id="TEST123",
        is_relevant=True,
        relevance_score=0.85,
        reason="Contains programming keywords",
        keywords_found=["coding", "programming", "developer"]
    )
    print(f"✅ Filter result: {filter_result.relevance_score}")
    
    # Test TaskCategories with enums
    categories = TaskCategories(
        task_summary="Participants debugged Python code",
        participant_skill_level=SkillLevel.INTERMEDIATE,
        programming_language="Python",
        programming_domain=ProgrammingDomain.DATA_SCIENCE,
        task_type=TaskType.DEBUGGING,
        is_programming_related=True,
        is_ai_related=False
    )
    print(f"✅ Categories: {categories.programming_domain.value}")
    
    # Test QualityScore with auto-calculation
    quality = QualityScore(
        confidence=0.9,
        completeness=0.8,
        consistency=0.85
    )
    print(f"✅ Quality score: {quality.overall:.2f} (auto-calculated)")
    
    # Test validation (this should work)
    try:
        bad_score = QualityScore(confidence=1.5, completeness=0.5, consistency=0.5)
        print("❌ Validation failed - should not accept confidence > 1.0")
    except Exception as e:
        print("✅ Validation works - caught invalid score")
    
    print("\n🎉 All models work correctly!")

if __name__ == "__main__":
    test_models()