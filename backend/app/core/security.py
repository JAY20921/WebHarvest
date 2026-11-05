"""
Security Service
Centralized security checks and utilities
"""

from app.utils.url_validator import (
    validate_url,
    validate_and_normalize_url,
    URLValidationError,
    SSRFProtectionError
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Security service for handling URL validation and SSRF protection
    """
    
    @staticmethod
    async def validate_extraction_url(url: str) -> dict:
        """
        Validate URL for extraction with comprehensive security checks
        
        Args:
            url: URL to validate
            
        Returns:
            Validation result dictionary
            
        Raises:
            URLValidationError: If URL format is invalid
            SSRFProtectionError: If URL is blocked
        """
        logger.info(f"Validating URL: {url}")
        
        # Perform validation
        result = await validate_and_normalize_url(url)
        
        if not result["is_valid"]:
            error_msg = result.get("error", "Unknown validation error")
            logger.error(f"URL validation failed: {error_msg}")
            
            # Determine exception type
            if "SSRF" in error_msg or "blocked" in error_msg.lower():
                raise SSRFProtectionError(error_msg)
            else:
                raise URLValidationError(error_msg)
        
        logger.info(f"URL validated successfully: {url} -> {result['resolved_ip']}")
        return result
    
    @staticmethod
    def is_ssrf_protection_enabled() -> bool:
        """Check if SSRF protection is enabled"""
        return settings.ENABLE_SSRF_PROTECTION
    
    @staticmethod
    def get_security_status() -> dict:
        """
        Get current security configuration status
        
        Returns:
            Dictionary with security settings
        """
        return {
            "ssrf_protection_enabled": settings.ENABLE_SSRF_PROTECTION,
            "block_private_ips": settings.BLOCK_PRIVATE_IPS,
            "block_cloud_metadata": settings.BLOCK_CLOUD_METADATA,
            "allowed_schemes": settings.ALLOWED_URL_SCHEMES.split(','),
        }


# Create singleton instance
security_service = SecurityService()
