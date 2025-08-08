"""
PaperFilter: Smart pre-filtering to identify papers likely to contain coding tasks.

This component uses keyword-based scoring to quickly identify papers that are worth
processing with expensive LLM calls. Based on analysis of CHI papers, ~86% can be
filtered out early, saving significant API costs.
"""

from typing import List, Dict
from ..models.task_models import Paper, FilterResult


class PaperFilter:
    """Filters papers based on relevance to coding tasks."""
    
    def __init__(self):
        """Initialize the filter with keyword scoring rules."""
        
        # High-value keywords that strongly indicate coding tasks
        self.high_relevance_keywords = {
            # Core programming terms - these are STRONG indicators
            'programming': 0.4, 'code': 0.4, 'coding': 0.4, 'programmer': 0.4,
            'debug': 0.4, 'debugging': 0.4, 'implementation': 0.3, 'software development': 0.4,
            
            # AI/Code generation (very common in recent CHI papers)
            'code generators': 0.5, 'code generation': 0.5, 'ai code': 0.5, 'copilot': 0.5,
            
            # Development tools and environments
            'IDE': 0.4, 'compiler': 0.4, 'visual studio': 0.4, 'eclipse': 0.4,
            
            # Clear study methodology indicators
            'participants implemented': 0.5, 'participants coded': 0.5, 'coding task': 0.5,
            'programming task': 0.5, 'participants debugged': 0.5
        }
        
        # Medium-value keywords - need more context to be meaningful
        self.medium_relevance_keywords = {
            # Study indicators (but could be any HCI study)
            'user study': 0.2, 'experiment': 0.2, 'participants performed': 0.2,
            'participants were asked': 0.2,
            
            # Technical terms that MIGHT indicate programming (need caution)
            'algorithm': 0.2, 'framework': 0.2, 'library': 0.2, 'API': 0.2,
            'application': 0.1, 'software': 0.1
        }
        
        # Negative keywords that indicate non-coding papers
        self.negative_keywords = {
            # Review/survey papers (rarely have user studies)
            'review': -0.4, 'survey': -0.4, 'analysis of': -0.4, 
            'scoping': -0.4, 'literature': -0.3, 'systematic review': -0.5,
            'meta-analysis': -0.4, 'multidisciplinary': -0.3,
            
            # Research method papers (analyze but don't code)
            'thematic analysis': -0.4, 'qualitative': -0.3, 'ethnographic': -0.3,
            'interview': -0.2, 'focus group': -0.3,
            
            # Physical/tangible interaction (usually not coding)
            'tangible': -0.1, 'haptic': -0.1, 'gesture': -0.1, 'embodied': -0.2,
            
            # Domain areas less likely to have coding tasks
            'agriculture': -0.2, 'healthcare': -0.1, 'medical': -0.1, 
            'accessibility': -0.1, 'privacy': -0.1,
            
            # Generic HCI terms that appear everywhere
            'design': 0.0, 'interface': 0.0, 'user': 0.0, 'tool': 0.0, 
            'system': 0.0, 'model': 0.0, 'method': 0.0, 'approach': 0.0,
            'interaction': 0.0, 'evaluation': 0.0, 'technique': 0.0, 'learning': 0.0
        }
        
        # Combine all keywords for easy searching
        self.all_keywords = {
            **self.high_relevance_keywords,
            **self.medium_relevance_keywords, 
            **self.negative_keywords
        }
    
    def _calculate_keyword_score(self, text: str) -> tuple[float, List[str]]:
        """Calculate relevance score based on keyword presence in text."""
        if not text:
            return 0.0, []
            
        text_lower = text.lower()
        score = 0.0
        found_keywords = []
        
        # Check each keyword
        for keyword, weight in self.all_keywords.items():
            if keyword in text_lower:
                score += weight
                found_keywords.append(keyword)
        
        # Normalize score to 0-1 range (clamp between 0 and 1)
        # Based on analysis, scores typically range from -0.5 to +1.0
        normalized_score = max(0.0, min(1.0, (score + 0.5) / 1.5))
        
        return normalized_score, found_keywords
    
    def _extract_keywords_from_paper(self, paper: Paper) -> str:
        """Extract searchable text from paper title and abstract."""
        searchable_text = ""
        
        if paper.title:
            searchable_text += paper.title + " "
        
        if paper.abstract:
            searchable_text += paper.abstract
            
        return searchable_text.strip()
    
    def _determine_relevance(self, score: float, keywords: List[str]) -> tuple[bool, str]:
        """Determine if paper is relevant based on score and provide reasoning."""
        
        if score >= 0.6:
            return True, f"High relevance score ({score:.2f}) with strong keywords: {', '.join(keywords[:3])}"
        elif score >= 0.3:
            return True, f"Medium relevance score ({score:.2f}) - borderline case worth checking"
        else:
            negative_keywords = [k for k in keywords if self.all_keywords.get(k, 0) < 0]
            if negative_keywords:
                return False, f"Low relevance ({score:.2f}) with negative indicators: {', '.join(negative_keywords[:2])}"
            else:
                return False, f"Low relevance score ({score:.2f}) - insufficient programming indicators"
    
    def filter_paper(self, paper: Paper) -> FilterResult:
        """Filter a single paper and return relevance assessment."""
        
        # Extract searchable text
        searchable_text = self._extract_keywords_from_paper(paper)
        
        # Calculate keyword-based score
        score, found_keywords = self._calculate_keyword_score(searchable_text)
        
        # Determine relevance and reasoning
        is_relevant, reason = self._determine_relevance(score, found_keywords)
        
        return FilterResult(
            paper_id=paper.paper_id,
            is_relevant=is_relevant,
            relevance_score=score,
            reason=reason,
            keywords_found=found_keywords
        )
    
    def filter_papers(self, papers: List[Paper]) -> List[FilterResult]:
        """Filter a list of papers and return results."""
        return [self.filter_paper(paper) for paper in papers]
    
    def get_relevant_papers(self, papers: List[Paper]) -> List[Paper]:
        """Get only the papers that pass the relevance filter."""
        results = self.filter_papers(papers)
        relevant_ids = {r.paper_id for r in results if r.is_relevant}
        return [p for p in papers if p.paper_id in relevant_ids]
    
    def get_stats(self, results: List[FilterResult]) -> Dict[str, float]:
        """Get filtering statistics."""
        if not results:
            return {}
            
        total = len(results)
        relevant = sum(1 for r in results if r.is_relevant)
        avg_score = sum(r.relevance_score for r in results) / total
        
        return {
            'total_papers': total,
            'relevant_papers': relevant,
            'filtered_out': total - relevant,
            'relevance_rate': relevant / total,
            'filter_rate': (total - relevant) / total,
            'avg_relevance_score': avg_score
        }