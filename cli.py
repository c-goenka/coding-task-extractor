"""Command-line interface for the simplified pipeline."""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.models.task_models import Paper
from pipeline import SimplifiedPipeline
from src.utils.data_helpers import load_papers_from_csv, save_results_to_csv


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Simplified Coding Task Extraction Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py papers.csv --output results.csv
  python cli.py papers.csv --output results.csv --model gpt-4o-mini --threshold-low 0.2
  python cli.py papers.csv --output results.csv --limit 50
        """
    )
    
    parser.add_argument('input_csv', help='Input CSV file with papers')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file for results')
    parser.add_argument('--model', default='gpt-4o-mini', help='LLM model to use (default: gpt-4o-mini)')
    parser.add_argument('--temperature', type=float, default=0.2, help='LLM temperature (default: 0.2)')
    parser.add_argument('--threshold-low', type=float, default=0.3, help='Filter threshold low (default: 0.3)')
    parser.add_argument('--threshold-high', type=float, default=0.6, help='Filter threshold high (default: 0.6)')
    parser.add_argument('--limit', type=int, help='Limit number of papers to process')
    parser.add_argument('--skip-no-abstracts', action='store_true', help='Skip papers without abstracts')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode - minimal output')
    
    args = parser.parse_args()
    
    # Check input file exists
    if not Path(args.input_csv).exists():
        print(f"Error: Input file '{args.input_csv}' not found")
        return 1
    
    # Load papers
    if not args.quiet:
        print(f"Loading papers from: {args.input_csv}")
    
    try:
        papers = load_papers_from_csv(args.input_csv, limit=args.limit, skip_no_abstracts=args.skip_no_abstracts)
            
        if not args.quiet:
            print(f"Loaded {len(papers)} papers")
        
    except Exception as e:
        print(f"Error loading papers: {e}")
        return 1
    
    # Initialize pipeline
    pipeline = SimplifiedPipeline(
        model=args.model,
        temperature=args.temperature,
        filter_threshold_low=args.threshold_low,
        filter_threshold_high=args.threshold_high
    )
    
    if not pipeline.extractor.llm_available:
        print("Error: LLM not available. Please check your OpenAI API key.")
        print("Set OPENAI_API_KEY environment variable or create .env file")
        return 1
    
    # Process papers
    if not args.quiet:
        print(f"Processing papers with model: {args.model}")
        print(f"Filter thresholds: {args.threshold_low} - {args.threshold_high}")
    
    try:
        results = pipeline.process_papers(papers, show_progress=not args.quiet)
        
        if not args.quiet:
            pipeline.print_summary(results)
        
        # Save results
        save_results_to_csv(results, args.output)
        
        if not args.quiet:
            print(f"\n✅ Pipeline completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"Error processing papers: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())