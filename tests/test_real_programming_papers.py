"""Test the pipeline on papers we know have coding tasks."""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task_models import Paper
from pipeline import SimplifiedPipeline

def test_real_programming_papers():
    """Test on papers that definitely have coding tasks."""
    
    print("=== TESTING ON REAL PROGRAMMING PAPERS ===\n")
    
    # Load data and get programming papers
    df = pd.read_csv('../data/chi_23/results/results_chi_23_intermediate.csv')
    
    # Get papers that have coding tasks in the current system
    programming_papers = df[df['coding_task'] != 'Not found'].head(3)
    
    papers = []
    for _, row in programming_papers.iterrows():
        paper = Paper(
            paper_id=row['paper_id'],
            title=row['title'],
            authors=row['authors'],
            venue=row['venue'],
            year=row['year'],
            abstract=row['abstract'] if pd.notna(row['abstract']) else ""
        )
        papers.append(paper)
    
    print("Testing on programming papers from current system:")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper.paper_id}: {paper.title[:60]}...")
    
    print("\n" + "="*70)
    
    # Run pipeline
    pipeline = SimplifiedPipeline(
        filter_threshold_low=0.2,   # Lower threshold to be more inclusive
        filter_threshold_high=0.7   # Higher threshold for auto-accept
    )
    
    if not pipeline.extractor.llm_available:
        print("❌ LLM not available")
        return
    
    print("🚀 Running simplified pipeline...\n")
    
    results = pipeline.process_papers(papers, show_progress=True)
    
    # Show detailed results
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in results:
        print(f"\n📄 {result.paper.paper_id}: {result.paper.title[:50]}...")
        
        # Filter stage
        filter_score = result.filter_result.relevance_score
        filter_relevant = result.filter_result.is_relevant
        keywords = result.filter_result.keywords_found[:3]
        print(f"   🔍 Filter: {filter_score:.2f} ({'✅ Relevant' if filter_relevant else '❌ Filtered'}) - {', '.join(keywords)}")
        
        # Binary classification
        if result.extraction_result:
            has_coding = result.extraction_result.has_coding_task  
            confidence = result.extraction_result.confidence
            reason = result.extraction_result.extraction_reason
            print(f"   🤖 Binary: {'✅ YES' if has_coding else '❌ NO'} (confidence: {confidence:.2f})")
            print(f"       Reason: {reason[:80]}...")
            
            # If YES, we should have categories
            if has_coding and result.categories:
                print(f"   📋 Categories:")
                print(f"       Language: {result.categories.programming_language or 'Not specified'}")
                print(f"       Domain: {result.categories.programming_domain.value if result.categories.programming_domain else 'Not specified'}")
                print(f"       Task Type: {result.categories.task_type.value if result.categories.task_type else 'Not specified'}")
                print(f"       Skill Level: {result.categories.participant_skill_level.value if result.categories.participant_skill_level else 'Not specified'}")
                
                # Quality score
                if result.quality_score:
                    quality = result.quality_score.overall
                    print(f"   📊 Quality: {quality:.2f} (conf: {result.quality_score.confidence:.2f}, comp: {result.quality_score.completeness:.2f})")
        
        print(f"   ⏱️  Time: {result.processing_time:.1f}s")
    
    # Final summary
    pipeline.print_summary(results)
    
    # Count successes
    successful_extractions = sum(1 for r in results if r.has_valid_task)
    total_papers = len(results)
    
    print(f"\n🎯 SUCCESS ANALYSIS:")
    print(f"   Papers processed: {total_papers}")
    print(f"   Successful extractions: {successful_extractions}")
    print(f"   Success rate: {successful_extractions/total_papers*100:.1f}%")
    
    if successful_extractions > 0:
        print(f"   ✅ Pipeline successfully extracted and categorized programming tasks!")
    else:
        print(f"   ⚠️  No successful extractions - may need prompt refinement")

if __name__ == "__main__":
    test_real_programming_papers()