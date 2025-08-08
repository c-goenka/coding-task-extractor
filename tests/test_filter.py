"""Test the PaperFilter on real CHI data to validate our approach."""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task_models import Paper, FilterResult
from typing import List, Dict

def test_paper_filter():
    """Test the paper filter on actual CHI data."""
    
    # Load actual results to see ground truth
    df = pd.read_csv('../data/chi_23/results/results_chi_23_intermediate.csv')
    
    # Create Paper objects from the data
    papers = []
    ground_truth = {}  # paper_id -> has_coding_task
    
    for _, row in df.head(20).iterrows():  # Test on first 20 papers
        paper = Paper(
            paper_id=row['paper_id'],
            title=row['title'],
            authors=row['authors'],
            venue=row['venue'], 
            year=row['year'],
            abstract=row['abstract'] if pd.notna(row['abstract']) else ""
        )
        papers.append(paper)
        ground_truth[row['paper_id']] = row['coding_task'] != 'Not found'
    
    # Import and test the filter
    from core.paper_filter import PaperFilter
    filter = PaperFilter()
    results = filter.filter_papers(papers)
    
    # Show results
    print("=== PAPER FILTER TEST RESULTS ===")
    print(f"Testing on {len(papers)} papers")
    
    correct_predictions = 0
    
    for result, paper in zip(results, papers):
        actual_has_coding = ground_truth[paper.paper_id]
        predicted_relevant = result.is_relevant
        
        # Check if our prediction matches reality
        correct = predicted_relevant == actual_has_coding
        if correct:
            correct_predictions += 1
            
        status = "✅" if correct else "❌"
        
        print(f"\n{status} {paper.paper_id}")
        print(f"   Title: {paper.title[:60]}...")
        print(f"   Predicted: {'Relevant' if predicted_relevant else 'Not relevant'} ({result.relevance_score:.2f})")
        print(f"   Actual: {'Has coding' if actual_has_coding else 'No coding'}")
        print(f"   Keywords: {', '.join(result.keywords_found[:3])}")
        print(f"   Reason: {result.reason}")
    
    # Overall statistics
    accuracy = correct_predictions / len(papers)
    stats = filter.get_stats(results)
    
    print(f"\n=== OVERALL PERFORMANCE ===")
    print(f"Accuracy: {accuracy:.1%} ({correct_predictions}/{len(papers)})")
    print(f"Papers marked relevant: {stats['relevant_papers']}/{stats['total_papers']}")
    print(f"Filter rate: {stats['filter_rate']:.1%}")
    print(f"Average relevance score: {stats['avg_relevance_score']:.2f}")

if __name__ == "__main__":
    test_paper_filter()