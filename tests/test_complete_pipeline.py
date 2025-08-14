"""Test the complete simplified pipeline end-to-end."""

import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task_models import Paper
from pipeline import SimplifiedPipeline

def test_complete_pipeline():
    """Test the complete pipeline on a small sample of papers."""

    print("=== SIMPLIFIED PIPELINE END-TO-END TEST ===\n")

    # Load some test papers
    try:
        df = pd.read_csv('../data/chi_23/results/results_chi_23_intermediate.csv')
    except FileNotFoundError:
        print("❌ Test data not found. Please ensure CHI data is available.")
        return

    # Get a small sample - mix of programming and non-programming papers
    sample_papers = []

    # Get 2 clear programming papers
    coding_papers = df[df['coding_task'] != 'Not found'].head(2)
    for _, row in coding_papers.iterrows():
        paper = Paper(
            paper_id=row['paper_id'],
            title=row['title'],
            authors=row['authors'],
            venue=row['venue'],
            year=row['year'],
            abstract=row['abstract'] if pd.notna(row['abstract']) else ""
        )
        sample_papers.append(paper)

    # Get 3 non-programming papers
    non_coding_papers = df[df['coding_task'] == 'Not found'].head(3)
    for _, row in non_coding_papers.iterrows():
        paper = Paper(
            paper_id=row['paper_id'],
            title=row['title'],
            authors=row['authors'],
            venue=row['venue'],
            year=row['year'],
            abstract=row['abstract'] if pd.notna(row['abstract']) else ""
        )
        sample_papers.append(paper)

    print(f"Testing pipeline on {len(sample_papers)} papers:")
    for i, paper in enumerate(sample_papers, 1):
        print(f"  {i}. {paper.title[:60]}...")

    print("\n" + "="*60)

    # Initialize and run pipeline
    try:
        pipeline = SimplifiedPipeline(
            model="gpt-4o-mini",
            temperature=0.2,
            filter_threshold_low=0.3,
            filter_threshold_high=0.6
        )

        if not pipeline.extractor.llm_available:
            print("❌ LLM not available. Please check OpenAI API key setup.")
            print("   Set OPENAI_API_KEY in environment or .env file")
            return

        print("🚀 Running complete pipeline...\n")

        # Process papers
        results = pipeline.process_papers(sample_papers, show_progress=True)

        # Show individual results
        print("\n" + "="*60)
        print("INDIVIDUAL RESULTS")
        print("="*60)

        for result in results:
            print(f"\n📄 {result.paper.paper_id}: {result.paper.title[:50]}...")

            # Filter result
            filter_score = result.filter_result.relevance_score
            filter_decision = "✅ Relevant" if result.filter_result.is_relevant else "❌ Filtered out"
            print(f"   Filter: {filter_decision} (score: {filter_score:.2f})")

            # Extraction result
            if result.extraction_result:
                extraction_decision = "✅ Programming" if result.extraction_result.has_coding_task else "❌ No coding"
                confidence = result.extraction_result.confidence
                print(f"   Extraction: {extraction_decision} (confidence: {confidence:.2f})")

            # Categories
            if result.categories:
                lang = result.categories.programming_language or "Not specified"
                domain = result.categories.programming_domain.value if result.categories.programming_domain else "Not specified"
                print(f"   Language: {lang}")
                print(f"   Domain: {domain}")

            # Quality score
            if result.quality_score:
                quality = result.quality_score.overall
                quality_level = "🟢 High" if quality >= 0.7 else "🟡 Medium" if quality >= 0.4 else "🔴 Low"
                print(f"   Quality: {quality_level} ({quality:.2f})")

            print(f"   Processing time: {result.processing_time:.1f}s")

        # Show summary
        pipeline.print_summary(results)

        print("\n🎉 Pipeline test completed successfully!")

        return results

    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_complete_pipeline()
