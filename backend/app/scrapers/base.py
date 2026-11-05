"""
Base Scraper Abstract Class
Defines interface that all scrapers must implement
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ScrapedPage:
    """
    Data class representing a scraped webpage
    """
    url: str
    final_url: str  # After redirects
    html: str
    status_code: int
    headers: Dict[str, str]
    content_type: str
    size_bytes: int
    load_time_seconds: float
    metadata: Dict[str, Any]  # Additional scraper-specific metadata
    
    def __repr__(self):
        return f"<ScrapedPage(url={self.url}, size={self.size_bytes} bytes, status={self.status_code})>"


class Scraper(ABC):
    """
    Abstract base class for all web scrapers
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    @abstractmethod
    async def fetch(self, url: str) -> ScrapedPage:
        """
        Fetch webpage content
        
        Args:
            url: URL to fetch
            
        Returns:
            ScrapedPage object with content and metadata
            
        Raises:
            ScrapingError: If fetching fails
        """
        pass
    
    @abstractmethod
    async def close(self):
        """
        Clean up resources (close connections, browsers, etc.)
        Must be called when done with scraper
        """
        pass
    
    @abstractmethod
    def supports_javascript(self) -> bool:
        """
        Check if this scraper can handle JavaScript-rendered pages
        
        Returns:
            True if JavaScript is supported, False otherwise
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
