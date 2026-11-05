"""
Scraping Service - High-level orchestration of web scraping
"""

from typing import Optional, Dict, Any
from app.scrapers.base import Scraper, ScrapedPage
from app.scrapers.http_scraper import HTTPScraper
from app.scrapers.browser_scraper import BrowserScraper
from app.scrapers.html_parser import HTMLParser
from app.scrapers.dom_analyzer import DOMAnalyzer
from app.core.config import settings
from app.core.exceptions import ScrapingError
import logging

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    High-level service for web scraping operations
    Handles scraper selection, execution, and content analysis
    """
    
    def __init__(self):
        """Initialize scraping service"""
        self._http_scraper: Optional[HTTPScraper] = None
        self._browser_scraper: Optional[BrowserScraper] = None
    
    def _should_use_browser(self, url: str) -> bool:
        """
        Determine if browser scraping is needed
        
        Args:
            url: URL to check
            
        Returns:
            True if browser should be used, False for HTTP
        """
        # Heuristics for when to use browser
        # In MVP, we'll try HTTP first, fall back to browser on failure
        # Future: Could maintain a database of known JS-heavy domains
        
        # Known JS-heavy patterns
        js_indicators = [
            'javascript',
            'react',
            'angular',
            'vue',
            'spa',
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in js_indicators)
    
    async def scrape_url(
        self, 
        url: str, 
        force_browser: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape URL and return comprehensive result
        
        Args:
            url: URL to scrape
            force_browser: Force use of browser scraper
            
        Returns:
            Dictionary with scraped data and analysis
            {
                'page': ScrapedPage object,
                'parser': HTMLParser object,
                'analyzer': DOMAnalyzer object,
                'summary': Page summary for LLM,
                'metadata': Extracted metadata,
            }
            
        Raises:
            ScrapingError: If scraping fails
        """
        logger.info(f"Starting scrape for: {url}")
        
        scraper: Optional[Scraper] = None
        page: Optional[ScrapedPage] = None
        
        try:
            # Determine which scraper to use
            use_browser = force_browser or self._should_use_browser(url)
            
            if use_browser:
                logger.info("Using browser scraper (JavaScript support)")
                scraper = await self._get_browser_scraper()
            else:
                logger.info("Using HTTP scraper (static HTML)")
                scraper = await self._get_http_scraper()
            
            # Fetch page
            try:
                page = await scraper.fetch(url)
            except ScrapingError as e:
                # If HTTP failed and we haven't tried browser yet, try browser
                if not use_browser and "timeout" not in str(e).lower():
                    logger.warning(f"HTTP scraping failed, trying browser: {e}")
                    scraper = await self._get_browser_scraper()
                    page = await scraper.fetch(url)
                else:
                    raise
            
            # Parse HTML
            parser = HTMLParser(page.html)
            
            # Analyze DOM
            analyzer = DOMAnalyzer(page.html)
            summary = analyzer.create_summary()
            
            # Extract metadata
            metadata = parser.get_metadata()
            
            logger.info(f"Successfully scraped {url}")
            
            return {
                'page': page,
                'parser': parser,
                'analyzer': analyzer,
                'summary': summary,
                'metadata': metadata,
                'scraper_type': 'browser' if use_browser else 'http',
            }
            
        except ScrapingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise ScrapingError(f"Scraping failed: {str(e)}")
    
    async def _get_http_scraper(self) -> HTTPScraper:
        """Get or create HTTP scraper instance"""
        if self._http_scraper is None:
            self._http_scraper = HTTPScraper()
        return self._http_scraper
    
    async def _get_browser_scraper(self) -> BrowserScraper:
        """Get or create browser scraper instance"""
        if self._browser_scraper is None:
            self._browser_scraper = BrowserScraper()
        return self._browser_scraper
    
    async def close(self):
        """Close all scrapers and clean up resources"""
        if self._http_scraper:
            await self._http_scraper.close()
            self._http_scraper = None
        
        if self._browser_scraper:
            await self._browser_scraper.close()
            self._browser_scraper = None
        
        logger.info("ScrapingService closed")


# Create singleton instance
scraping_service = ScrapingService()
