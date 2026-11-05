"""
HTTP Scraper using HTTPX
For static HTML pages that don't require JavaScript rendering
"""

import time
import httpx
from typing import Optional
from app.scrapers.base import Scraper, ScrapedPage
from app.core.config import settings
from app.core.exceptions import ScrapingError
import logging

logger = logging.getLogger(__name__)


class HTTPScraper(Scraper):
    """
    Fast scraper for static HTML pages using HTTPX
    Does not execute JavaScript
    """
    
    def __init__(self, timeout: int = None):
        """
        Initialize HTTP scraper
        
        Args:
            timeout: Request timeout in seconds (default from settings)
        """
        super().__init__(timeout or settings.SCRAPING_TIMEOUT_SECONDS)
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTPX client with proper configuration
        
        Returns:
            Configured HTTPX async client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                max_redirects=5,
                headers={
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/120.0.0.0 Safari/537.36'
                    ),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
            )
        return self._client
    
    async def fetch(self, url: str) -> ScrapedPage:
        """
        Fetch webpage using HTTP request
        
        Args:
            url: URL to fetch
            
        Returns:
            ScrapedPage with HTML content
            
        Raises:
            ScrapingError: If request fails
        """
        logger.info(f"HTTPScraper fetching: {url}")
        start_time = time.time()
        
        try:
            client = self._get_client()
            
            # Make request
            response = await client.get(url)
            response.raise_for_status()
            
            load_time = time.time() - start_time
            
            # Extract content
            html = response.text
            size_bytes = len(html.encode('utf-8'))
            
            # Check size limit
            max_size_bytes = settings.MAX_PAGE_SIZE_MB * 1024 * 1024
            if size_bytes > max_size_bytes:
                raise ScrapingError(
                    f"Page size ({size_bytes / (1024 * 1024):.2f} MB) "
                    f"exceeds limit ({settings.MAX_PAGE_SIZE_MB} MB)"
                )
            
            logger.info(
                f"HTTPScraper fetched {url} successfully "
                f"({size_bytes} bytes in {load_time:.2f}s)"
            )
            
            return ScrapedPage(
                url=url,
                final_url=str(response.url),
                html=html,
                status_code=response.status_code,
                headers=dict(response.headers),
                content_type=response.headers.get('content-type', ''),
                size_bytes=size_bytes,
                load_time_seconds=load_time,
                metadata={
                    'scraper_type': 'http',
                    'redirected': str(response.url) != url,
                    'redirect_count': len(response.history),
                }
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
            raise ScrapingError(
                f"HTTP {e.response.status_code} error: {e.response.reason_phrase}"
            )
        
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            raise ScrapingError(f"Request timeout after {self.timeout} seconds")
        
        except httpx.RequestError as e:
            logger.error(f"Request error fetching {url}: {e}")
            raise ScrapingError(f"Request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            raise ScrapingError(f"Scraping failed: {str(e)}")
    
    async def close(self):
        """Close HTTP client and clean up resources"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTPScraper closed")
    
    def supports_javascript(self) -> bool:
        """HTTP scraper does not support JavaScript"""
        return False
