"""
Abstract fetching utility to retrieve missing abstracts from DOI/URL sources.

Supports:
- ACM Digital Library
- IEEE Xplore  
- Springer
- Other common academic venues
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import re
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbstractFetcher:
    """Fetches abstracts from academic paper URLs/DOIs."""
    
    def __init__(self, cache_dir: str = "data/abstract_cache", delay: float = 1.0):
        """
        Initialize the abstract fetcher.
        
        Args:
            cache_dir: Directory to store cached abstracts
            delay: Delay between requests to be respectful
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Load existing cache
        self.cache_file = self.cache_dir / "abstract_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cached abstracts from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def _clean_abstract(self, text: str) -> str:
        """Clean and normalize abstract text."""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common prefixes
        text = re.sub(r'^(Abstract[:\-\s]*|ABSTRACT[:\-\s]*)', '', text, flags=re.IGNORECASE)
        
        # Remove trailing dots if they seem like artifacts
        text = re.sub(r'\.\.\.$', '', text)
        
        return text.strip()
    
    def fetch_from_acm(self, url: str) -> Optional[str]:
        """Fetch abstract from ACM Digital Library."""
        try:
            # Add referer and additional headers for ACM
            headers = {
                'Referer': 'https://dl.acm.org/',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            response = self.session.get(url, timeout=15, headers=headers)
            
            # Don't raise for status - handle different codes
            if response.status_code == 403:
                logger.warning(f"Access denied (403) for ACM URL: {url}")
                return None
            elif response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for ACM URL: {url}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for ACM abstracts
            selectors = [
                'div.abstractSection p',
                'div[data-test="abstract"] p',
                'div.abstract-text p',
                'div.abstract p',
                '.abstractSection',
                '.abstract-content'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    abstract_text = ' '.join(elem.get_text().strip() for elem in elements)
                    if len(abstract_text) > 50:  # Reasonable abstract length
                        return self._clean_abstract(abstract_text)
            
            # Fallback: look for any element with "abstract" in class/id
            abstract_elements = soup.find_all(attrs={"class": re.compile(r"abstract", re.I)})
            for elem in abstract_elements:
                text = elem.get_text().strip()
                if len(text) > 50:
                    return self._clean_abstract(text)
                    
        except Exception as e:
            logger.warning(f"Failed to fetch from ACM {url}: {e}")
        
        return None
    
    def fetch_from_ieee(self, url: str) -> Optional[str]:
        """Fetch abstract from IEEE Xplore."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # IEEE abstract selectors
            selectors = [
                'div.abstract-text div',
                '.abstract-text',
                '.abstract-desktop-div',
                '.u-mb-1.stats-abstract-details'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    if len(text) > 50:
                        return self._clean_abstract(text)
                        
        except Exception as e:
            logger.warning(f"Failed to fetch from IEEE {url}: {e}")
        
        return None
    
    def fetch_from_springer(self, url: str) -> Optional[str]:
        """Fetch abstract from Springer."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Springer abstract selectors
            selectors = [
                'div#Abs1-content p',
                '.Abstract p',
                '.c-article-section__content p',
                'section[data-title="Abstract"] p'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    text = ' '.join(elem.get_text().strip() for elem in elements)
                    if len(text) > 50:
                        return self._clean_abstract(text)
                        
        except Exception as e:
            logger.warning(f"Failed to fetch from Springer {url}: {e}")
        
        return None
    
    def fetch_abstract(self, url: str, paper_id: str = None) -> Optional[str]:
        """
        Fetch abstract from URL.
        
        Args:
            url: URL to fetch from
            paper_id: Paper ID for caching
            
        Returns:
            Abstract text or None if not found
        """
        if not url or not isinstance(url, str):
            return None
        
        # Check cache first
        cache_key = paper_id or url
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if cached_result:  # Don't return empty string from cache
                return cached_result
        
        # Add delay to be respectful
        time.sleep(self.delay)
        
        logger.info(f"Fetching abstract from: {url}")
        
        abstract = None
        domain = urlparse(url).netloc.lower()
        
        # Route to appropriate fetcher based on domain
        if 'acm.org' in domain:
            abstract = self.fetch_from_acm(url)
        elif 'ieee' in domain:
            abstract = self.fetch_from_ieee(url)
        elif 'springer' in domain:
            abstract = self.fetch_from_springer(url)
        else:
            # Generic approach for other sites
            abstract = self._fetch_generic(url)
        
        # Cache result (even if None to avoid re-fetching)
        self.cache[cache_key] = abstract or ""
        self._save_cache()
        
        if abstract:
            logger.info(f"✅ Successfully fetched abstract ({len(abstract)} chars)")
        else:
            logger.warning(f"❌ Could not fetch abstract from {url}")
        
        return abstract
    
    def _fetch_generic(self, url: str) -> Optional[str]:
        """Generic abstract fetching for unknown sites."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Generic selectors that might contain abstracts
            selectors = [
                '[class*="abstract"]',
                '[id*="abstract"]',
                'meta[name="description"]',
                'meta[property="og:description"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements:
                    if elem.name == 'meta':
                        text = elem.get('content', '')
                    else:
                        text = elem.get_text().strip()
                    
                    if len(text) > 50:
                        return self._clean_abstract(text)
                        
        except Exception as e:
            logger.warning(f"Generic fetch failed for {url}: {e}")
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        successful_fetches = sum(1 for v in self.cache.values() if v)
        
        return {
            'total_cached': total_entries,
            'successful_fetches': successful_fetches,
            'cache_hit_rate': successful_fetches / total_entries if total_entries > 0 else 0,
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }