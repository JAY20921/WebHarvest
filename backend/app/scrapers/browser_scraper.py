"""
Browser Scraper using Playwright
For JavaScript-rendered pages and dynamic content
"""

import time
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from app.scrapers.base import Scraper, ScrapedPage
from app.core.config import settings
from app.core.exceptions import ScrapingError
import logging

logger = logging.getLogger(__name__)


class BrowserScraper(Scraper):
    """
    Full-featured browser scraper using Playwright (Chromium)
    Executes JavaScript and waits for dynamic content
    """
    
    def __init__(self, timeout: int = None):
        """
        Initialize browser scraper
        
        Args:
            timeout: Page load timeout in seconds (default from settings)
        """
        super().__init__(timeout or settings.BROWSER_TIMEOUT_SECONDS)
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
    
    async def _ensure_browser(self):
        """
        Ensure browser is launched and ready
        Lazy initialization for better resource management
        """
        if self._browser is None:
            logger.info("Launching Playwright browser (Chromium)...")
            
            # Start Playwright
            self._playwright = await async_playwright().start()
            
            # Launch browser
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Create context with realistic settings
            self._context = await self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            logger.info("Playwright browser ready")
    
    async def fetch(self, url: str) -> ScrapedPage:
        """
        Fetch webpage using headless browser
        
        Args:
            url: URL to fetch
            
        Returns:
            ScrapedPage with rendered HTML content
            
        Raises:
            ScrapingError: If browser operation fails
        """
        logger.info(f"BrowserScraper fetching: {url}")
        start_time = time.time()
        
        page: Optional[Page] = None
        
        try:
            # Ensure browser is ready
            await self._ensure_browser()
            
            # Create new page
            page = await self._context.new_page()
            
            # Set timeout
            page.set_default_timeout(self.timeout * 1000)  # Convert to milliseconds
            
            # Navigate to URL
            response = await page.goto(
                url,
                wait_until='networkidle',  # Wait for network to be idle
                timeout=self.timeout * 1000
            )
            
            # Wait a bit more for any late-loading content
            await asyncio.sleep(1)
            
            # Get final URL (after redirects)
            final_url = page.url
            
            # Get HTML content
            html = await page.content()
            size_bytes = len(html.encode('utf-8'))
            
            # Check size limit
            max_size_bytes = settings.MAX_PAGE_SIZE_MB * 1024 * 1024
            if size_bytes > max_size_bytes:
                raise ScrapingError(
                    f"Page size ({size_bytes / (1024 * 1024):.2f} MB) "
                    f"exceeds limit ({settings.MAX_PAGE_SIZE_MB} MB)"
                )
            
            load_time = time.time() - start_time
            
            # Get response headers
            headers = {}
            if response:
                headers = await response.all_headers()
            
            logger.info(
                f"BrowserScraper fetched {url} successfully "
                f"({size_bytes} bytes in {load_time:.2f}s)"
            )
            
            return ScrapedPage(
                url=url,
                final_url=final_url,
                html=html,
                status_code=response.status if response else 200,
                headers=headers,
                content_type=headers.get('content-type', ''),
                size_bytes=size_bytes,
                load_time_seconds=load_time,
                metadata={
                    'scraper_type': 'browser',
                    'redirected': final_url != url,
                    'javascript_enabled': True,
                }
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            raise ScrapingError(f"Page load timeout after {self.timeout} seconds")
        
        except Exception as e:
            logger.error(f"Browser error fetching {url}: {e}")
            raise ScrapingError(f"Browser scraping failed: {str(e)}")
        
        finally:
            # Close page to free resources
            if page:
                await page.close()
    
    async def close(self):
        """Close browser and clean up all resources"""
        if self._context:
            await self._context.close()
            self._context = None
        
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        logger.info("BrowserScraper closed")
    
    def supports_javascript(self) -> bool:
        """Browser scraper supports JavaScript"""
        return True
