"""Helper functions for data loading and processing."""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import os

from ..models.task_models import Paper
from .abstract_fetcher import AbstractFetcher
from .pdf_abstract_extractor import PDFAbstractExtractor


def load_papers_from_csv(csv_path: str, limit: int = None, skip_no_abstracts: bool = False, extract_from_pdfs: bool = False) -> List[Paper]:
    """
    Load papers from CSV file.
    
    Args:
        csv_path: Path to CSV file with paper data
        limit: Optional limit on number of papers to load
        skip_no_abstracts: If True, skip papers without abstracts
        extract_from_pdfs: If True, extract abstracts from PDF files
        
    Returns:
        List of Paper objects
    """
    df = pd.read_csv(csv_path)
    
    # Map different possible column names
    column_mapping = {
        'abstract': ['Abstract Note', 'abstract', 'Abstract'],
        'paper_id': ['Key', 'paper_id', 'id', 'ID'],
        'title': ['Title', 'title'],
        'authors': ['Author', 'authors', 'Authors'],
        'venue': ['Publication Title', 'venue', 'Venue'],
        'year': ['Publication Year', 'year', 'Year'],
        'url': ['Url', 'url', 'URL'],
        'pdf_path': ['File Attachments', 'pdf_path', 'file_path']
    }
    
    # Find actual column names
    actual_columns = {}
    for standard_name, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in df.columns:
                actual_columns[standard_name] = possible_name
                break
        if standard_name not in actual_columns:
            if standard_name in ['paper_id', 'title']:  # Required columns
                raise ValueError(f"Required column '{standard_name}' not found. Available: {list(df.columns)}")
    
    # Handle abstracts
    abstract_col = actual_columns.get('abstract')
    pdf_col = actual_columns.get('pdf_path')
    pdf_extractor = None
    
    if abstract_col:
        # Count missing abstracts
        missing_count = df[abstract_col].isna().sum()
        total_count = len(df)
        
        if missing_count > 0:
            print(f"⚠️  {missing_count}/{total_count} papers ({missing_count/total_count*100:.1f}%) have missing abstracts")
            
            if skip_no_abstracts:
                print(f"   Skipping papers without abstracts...")
                df = df[df[abstract_col].notna() & (df[abstract_col] != '')]
            elif extract_from_pdfs and pdf_col:
                print(f"   📄 Will extract missing abstracts from PDF files...")
                pdf_extractor = PDFAbstractExtractor(lines_after_abstract=25)
            else:
                print(f"   Will use title for papers without abstracts...")
    else:
        print("⚠️  No abstract column found - will use title only")
    
    if limit:
        df = df.head(limit)
    
    papers = []
    extracted_count = 0
    
    for i, (_, row) in enumerate(df.iterrows()):
        # Get abstract or use title as fallback
        abstract_text = ""
        paper_id = str(row[actual_columns['paper_id']]) if 'paper_id' in actual_columns else f"paper_{i+1}"
        
        if abstract_col and pd.notna(row[abstract_col]) and row[abstract_col].strip():
            abstract_text = row[abstract_col]
        else:
            # Try to extract from PDF if enabled
            if pdf_extractor and pdf_col:
                pdf_path = row[pdf_col] if pd.notna(row[pdf_col]) else None
                if pdf_path:
                    # Handle potential multiple PDF paths (semicolon separated)
                    pdf_paths = [p.strip() for p in str(pdf_path).split(';') if p.strip()]
                    
                    for pdf_file_path in pdf_paths:
                        if os.path.exists(pdf_file_path):
                            extracted_abstract = pdf_extractor.extract_from_pdf(pdf_file_path)
                            if extracted_abstract:
                                abstract_text = extracted_abstract
                                extracted_count += 1
                                if (extracted_count % 5 == 0):  # Progress update
                                    print(f"   📥 Extracted {extracted_count} abstracts from PDFs...")
                                break  # Found abstract, stop trying other PDF paths
            
            # If still no abstract, use title as fallback
            if not abstract_text:
                title_text = row[actual_columns['title']] if 'title' in actual_columns else ""
                abstract_text = f"Title: {title_text}"  # Prefix to indicate it's a title
        
        paper = Paper(
            paper_id=paper_id,
            title=row[actual_columns['title']] if 'title' in actual_columns else "Untitled",
            authors=row[actual_columns['authors']] if 'authors' in actual_columns else "Unknown",
            venue=row[actual_columns['venue']] if 'venue' in actual_columns else "Unknown",
            year=int(row[actual_columns['year']]) if 'year' in actual_columns and pd.notna(row[actual_columns['year']]) else 2023,
            url=row[actual_columns['url']] if 'url' in actual_columns and pd.notna(row[actual_columns['url']]) else None,
            abstract=abstract_text
        )
        papers.append(paper)
    
    # Report extraction results
    if pdf_extractor:
        print(f"   ✅ Successfully extracted {extracted_count} abstracts from PDFs")
        if extracted_count > 0:
            success_rate = extracted_count / missing_count * 100 if missing_count > 0 else 0
            print(f"   📊 Extraction success rate: {success_rate:.1f}% ({extracted_count}/{missing_count})")
    
    print(f"📚 Loaded {len(papers)} papers from {csv_path}")
    return papers


def save_results_to_csv(results: List, output_path: str) -> None:
    """
    Save pipeline results to CSV file.
    
    Args:
        results: List of PipelineResult objects
        output_path: Path to save CSV file
    """
    data = []
    
    for result in results:
        row = {
            # Original paper metadata
            'paper_id': result.paper.paper_id,
            'title': result.paper.title,
            'authors': result.paper.authors,
            'venue': result.paper.venue,
            'year': result.paper.year,
            'url': result.paper.url,
            'abstract': result.paper.abstract,
            
            # Filter results
            'filter_score': result.filter_result.relevance_score if result.filter_result else None,
            'filter_relevant': result.filter_result.is_relevant if result.filter_result else None,
            'filter_keywords': ', '.join(result.filter_result.keywords_found) if result.filter_result else None,
            
            # Extraction results
            'has_coding_task': result.extraction_result.has_coding_task if result.extraction_result else None,
            'extraction_confidence': result.extraction_result.confidence if result.extraction_result else None,
            'extraction_reason': result.extraction_result.extraction_reason if result.extraction_result else None,
            
            # Categories (if available)
            'task_summary': result.categories.task_summary if result.categories else None,
            'participant_skill_level': result.categories.participant_skill_level.value if result.categories and result.categories.participant_skill_level else None,
            'programming_language': result.categories.programming_language if result.categories else None,
            'programming_domain': result.categories.programming_domain.value if result.categories and result.categories.programming_domain else None,
            'programming_sub_domain': result.categories.programming_sub_domain if result.categories else None,
            'task_type': result.categories.task_type.value if result.categories and result.categories.task_type else None,
            'code_size_scope': result.categories.code_size_scope.value if result.categories and result.categories.code_size_scope else None,
            'evaluation_metrics': result.categories.evaluation_metrics if result.categories else None,
            'tools_environment': result.categories.tools_environment if result.categories else None,
            'research_focus': result.categories.research_focus if result.categories else None,
            'is_programming_related': result.categories.is_programming_related if result.categories else None,
            'is_ai_related': result.categories.is_ai_related if result.categories else None,
            
            # Quality scores
            'quality_confidence': result.quality_score.confidence if result.quality_score else None,
            'quality_completeness': result.quality_score.completeness if result.quality_score else None,
            'quality_consistency': result.quality_score.consistency if result.quality_score else None,
            'quality_overall': result.quality_score.overall if result.quality_score else None,
            
            # Processing metadata
            'processing_time': result.processing_time,
            'error_message': result.error_message
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")


def save_papers_with_abstracts_to_csv(papers: List[Paper], output_path: str) -> None:
    """
    Save papers with their abstracts to CSV file.
    Useful for saving papers after fetching missing abstracts.
    
    Args:
        papers: List of Paper objects
        output_path: Path to save CSV file
    """
    data = []
    
    for paper in papers:
        row = {
            'paper_id': paper.paper_id,
            'title': paper.title,
            'authors': paper.authors,
            'venue': paper.venue,
            'year': paper.year,
            'url': paper.url,
            'abstract': paper.abstract
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"📁 Updated papers saved to: {output_path}")


def extract_and_update_csv(input_csv: str, output_csv: str = None, limit: int = None) -> None:
    """
    Extract missing abstracts from PDFs and save updated CSV.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path (defaults to input_csv with '_updated' suffix)
        limit: Limit number of papers to process
    """
    if not output_csv:
        # Generate output filename
        input_path = Path(input_csv)
        output_csv = str(input_path.parent / f"{input_path.stem}_updated{input_path.suffix}")
    
    print(f"📄 Extracting missing abstracts from PDFs: {input_csv}")
    papers = load_papers_from_csv(input_csv, limit=limit, extract_from_pdfs=True)
    
    print(f"💾 Saving updated papers to: {output_csv}")
    save_papers_with_abstracts_to_csv(papers, output_csv)
    
    print("✅ Abstract extraction complete!")


def get_programming_papers_from_results(csv_path: str, limit: int = None) -> List[Paper]:
    """
    Load papers that have coding tasks from existing results CSV.
    
    Args:
        csv_path: Path to results CSV from current pipeline
        limit: Optional limit on papers to load
        
    Returns:
        List of Paper objects that have coding tasks
    """
    df = pd.read_csv(csv_path)
    
    # Filter to papers with coding tasks
    programming_df = df[df['coding_task'] != 'Not found']
    
    if limit:
        programming_df = programming_df.head(limit)
    
    papers = []
    for _, row in programming_df.iterrows():
        paper = Paper(
            paper_id=row['paper_id'],
            title=row['title'],
            authors=row['authors'],
            venue=row['venue'],
            year=row['year'],
            url=row.get('url', None),
            abstract=row['abstract'] if pd.notna(row['abstract']) else ""
        )
        papers.append(paper)
    
    return papers