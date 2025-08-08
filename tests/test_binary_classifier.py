"""Test the binary classification prompt on real papers."""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task_models import Paper
from core.task_extractor import TaskExtractor

def test_binary_classifier():
    """Test the binary classifier on papers with known ground truth."""
    
    # Load some test papers
    df = pd.read_csv('../data/chi_23/results/results_chi_23_intermediate.csv')
    
    # Get a mix of papers - some with coding tasks, some without
    test_cases = []
    
    # Get some clear programming papers
    coding_papers = df[df['coding_task'] != 'Not found'].head(3)
    for _, row in coding_papers.iterrows():
        test_cases.append({
            'paper': Paper(
                paper_id=row['paper_id'],
                title=row['title'],
                authors=row['authors'],
                venue=row['venue'],
                year=row['year'],
                abstract=row['abstract'] if pd.notna(row['abstract']) else ""
            ),
            'expected': True,
            'type': 'Programming'
        })
    
    # Get some clear non-programming papers
    non_coding_papers = df[df['coding_task'] == 'Not found'].head(3) 
    for _, row in non_coding_papers.iterrows():
        test_cases.append({
            'paper': Paper(
                paper_id=row['paper_id'],
                title=row['title'], 
                authors=row['authors'],
                venue=row['venue'],
                year=row['year'],
                abstract=row['abstract'] if pd.notna(row['abstract']) else ""
            ),
            'expected': False,
            'type': 'Non-Programming'
        })
    
    print("=== TESTING BINARY CLASSIFIER ===")
    print(f"Testing {len(test_cases)} papers")
    print()
    
    # Test with TaskExtractor
    extractor = TaskExtractor()
    
    if not extractor.llm_available:
        print("❌ LLM not available. Please check OpenAI API key setup.")
        return
    
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        paper = test_case['paper']
        expected = test_case['expected']
        paper_type = test_case['type']
        
        print(f"\n--- Test {i}/{total} ({paper_type}) ---")
        print(f"Title: {paper.title[:80]}...")
        print(f"Expected: {'YES' if expected else 'NO'}")
        
        # Get prediction
        result = extractor.classify_paper_binary(paper)
        predicted = result.has_coding_task
        confidence = result.confidence
        reason = result.extraction_reason
        
        # Check if correct
        is_correct = predicted == expected
        if is_correct:
            correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} Predicted: {'YES' if predicted else 'NO'} (confidence: {confidence:.2f})")
        print(f"Reason: {reason}")
    
    print(f"\n=== RESULTS ===")
    print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    print(f"Model: {extractor.model}")

if __name__ == "__main__":
    test_binary_classifier()