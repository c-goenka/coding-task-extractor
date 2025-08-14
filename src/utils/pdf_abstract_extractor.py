"""
PDF-based abstract extractor that searches for "abstract" keyword 
and extracts the following content.
"""

import fitz  # PyMuPDF
import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFAbstractExtractor:
    """Extracts abstracts from PDF files by searching for 'abstract' keyword."""
    
    def __init__(self, lines_after_abstract: int = 25):
        """
        Initialize PDF abstract extractor.
        
        Args:
            lines_after_abstract: Number of lines to extract after finding "abstract"
        """
        self.lines_after_abstract = lines_after_abstract
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common PDF artifacts
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\s*-\s*\n\s*', '', text)  # Remove hyphenated line breaks
        text = re.sub(r'\f', ' ', text)  # Remove form feeds
        
        # Remove URLs and DOIs if they appear at the start
        text = re.sub(r'^https?://\S+\s*', '', text)
        text = re.sub(r'^DOI:\s*\S+\s*', '', text, flags=re.IGNORECASE)
        
        # Remove leading abstract label if present
        text = re.sub(r'^(Abstract[:\-\s]*|ABSTRACT[:\-\s]*)', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _find_abstract_position(self, text: str) -> Optional[int]:
        """
        Find the position where the abstract starts.
        
        Returns the character position after the abstract keyword.
        """
        # Try different abstract patterns
        patterns = [
            r'\bAbstract\b\s*[:\-]?\s*',
            r'\bABSTRACT\b\s*[:\-]?\s*',
            r'\n\s*Abstract\s*\n',
            r'\n\s*ABSTRACT\s*\n',
            r'Abstract\s*—',  # Em dash
            r'ABSTRACT\s*—',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.end()
        
        return None
    
    def _extract_lines_after_position(self, text: str, start_pos: int) -> str:
        """Extract specified number of lines after the given position."""
        # Get text from start position
        remaining_text = text[start_pos:]
        
        # Split into lines and get the first N lines
        lines = remaining_text.split('\n')
        
        # Take the specified number of lines
        abstract_lines = lines[:self.lines_after_abstract]
        
        # Join back and clean
        abstract_text = ' '.join(abstract_lines)
        
        # Stop at common section headers that indicate end of abstract
        stop_patterns = [
            r'\b(Keywords?|Index Terms?|Categories and Subject Descriptors)\b',
            r'\b(Introduction|1\.\s*Introduction)\b',
            r'\b(Related Work|Background)\b',
            r'\b(Methodology|Method|Approach)\b',
            r'\bACM Classification\b',
        ]
        
        for pattern in stop_patterns:
            match = re.search(pattern, abstract_text, re.IGNORECASE)
            if match:
                abstract_text = abstract_text[:match.start()].strip()
                break
        
        return self._clean_text(abstract_text)
    
    def extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract abstract from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted abstract text or None if not found
        """
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Usually abstract is on the first page, but check first few pages
            pages_to_check = min(3, len(doc))
            
            for page_num in range(pages_to_check):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Find abstract position
                abstract_pos = self._find_abstract_position(text)
                if abstract_pos:
                    # Extract content after abstract
                    abstract_text = self._extract_lines_after_position(text, abstract_pos)
                    
                    # Validate that we got reasonable content
                    if len(abstract_text) > 50:  # At least 50 characters
                        doc.close()
                        logger.info(f"✅ Extracted abstract from {os.path.basename(pdf_path)} (page {page_num + 1})")
                        return abstract_text
            
            doc.close()
            logger.warning(f"❌ No abstract found in {os.path.basename(pdf_path)}")
            return None
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return None
    
    def extract_with_fallback_paths(self, pdf_path: str, alternative_paths: List[str] = None) -> Optional[str]:
        """
        Extract abstract with fallback to alternative file paths.
        
        Args:
            pdf_path: Primary PDF file path
            alternative_paths: List of alternative paths to try
            
        Returns:
            Extracted abstract text or None if not found
        """
        # Try primary path first
        abstract = self.extract_from_pdf(pdf_path)
        if abstract:
            return abstract
        
        # Try alternative paths
        if alternative_paths:
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    abstract = self.extract_from_pdf(alt_path)
                    if abstract:
                        return abstract
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics (placeholder for future implementation)."""
        return {
            'lines_after_abstract': self.lines_after_abstract,
            'extractor_ready': True
        }


def test_pdf_extraction():
    """Test PDF abstract extraction with sample files."""
    extractor = PDFAbstractExtractor(lines_after_abstract=25)
    
    # Test with any PDF files in data directory
    data_dir = Path("data")
    if data_dir.exists():
        pdf_files = list(data_dir.rglob("*.pdf"))
        
        if pdf_files:
            print(f"🧪 Testing PDF extraction with {len(pdf_files)} files...")
            
            for i, pdf_file in enumerate(pdf_files[:3]):  # Test first 3
                print(f"\n{i+1}. Testing: {pdf_file.name}")
                abstract = extractor.extract_from_pdf(str(pdf_file))
                
                if abstract:
                    print(f"   ✅ Extracted {len(abstract)} characters")
                    print(f"   Preview: {abstract[:150]}...")
                else:
                    print(f"   ❌ No abstract found")
        else:
            print("No PDF files found in data directory for testing")
    else:
        print("Data directory not found - skipping PDF tests")


if __name__ == "__main__":
    test_pdf_extraction()