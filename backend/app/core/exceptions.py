"""
Custom Exception Classes
"""


class IntelligentScraperException(Exception):
    """Base exception for all application errors"""
    pass


class URLValidationError(IntelligentScraperException):
    """Raised when URL validation fails"""
    pass


class SSRFProtectionError(IntelligentScraperException):
    """Raised when URL is blocked for SSRF protection"""
    pass


class ScrapingError(IntelligentScraperException):
    """Raised when web scraping fails"""
    pass


class LLMError(IntelligentScraperException):
    """Raised when LLM provider fails"""
    pass


class ExtractionError(IntelligentScraperException):
    """Raised when data extraction fails"""
    pass


class ExportError(IntelligentScraperException):
    """Raised when data export fails"""
    pass


class ValidationError(IntelligentScraperException):
    """Raised when data validation fails"""
    pass
