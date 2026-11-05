"""
URL Validation and SSRF Protection
Critical security module to prevent Server-Side Request Forgery attacks
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class URLValidationError(Exception):
    """Raised when URL validation fails"""
    pass


class SSRFProtectionError(Exception):
    """Raised when URL is blocked for SSRF protection"""
    pass


# Blocked IP ranges (RFC 1918 private networks, localhost, link-local)
BLOCKED_IP_RANGES = [
    ipaddress.ip_network("127.0.0.0/8"),      # Localhost
    ipaddress.ip_network("10.0.0.0/8"),       # Private network
    ipaddress.ip_network("172.16.0.0/12"),    # Private network
    ipaddress.ip_network("192.168.0.0/16"),   # Private network
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local
    ipaddress.ip_network("::1/128"),          # IPv6 localhost
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

# Blocked hostnames (cloud metadata endpoints)
BLOCKED_HOSTNAMES = [
    "metadata.google.internal",
    "169.254.169.254",
    "metadata",
    "localhost",
]


def is_ip_blocked(ip_str: str) -> bool:
    """
    Check if IP address is in blocked ranges
    
    Args:
        ip_str: IP address as string
        
    Returns:
        True if IP is blocked, False otherwise
    """
    if not settings.BLOCK_PRIVATE_IPS:
        return False
        
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Check against blocked ranges
        for blocked_range in BLOCKED_IP_RANGES:
            if ip in blocked_range:
                logger.warning(f"Blocked IP address: {ip_str} (in range {blocked_range})")
                return True
                
        return False
    except ValueError:
        # Invalid IP address
        return False


def is_hostname_blocked(hostname: str) -> bool:
    """
    Check if hostname is in blocked list
    
    Args:
        hostname: Hostname to check
        
    Returns:
        True if hostname is blocked, False otherwise
    """
    if not settings.BLOCK_CLOUD_METADATA:
        return False
        
    hostname_lower = hostname.lower()
    
    for blocked in BLOCKED_HOSTNAMES:
        if blocked in hostname_lower:
            logger.warning(f"Blocked hostname: {hostname}")
            return True
            
    return False


async def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address
    
    Args:
        hostname: Hostname to resolve
        
    Returns:
        IP address as string, or None if resolution fails
        
    Raises:
        SSRFProtectionError: If resolved IP is blocked
    """
    try:
        # Get IP address
        ip_str = socket.gethostbyname(hostname)
        
        # Check if IP is blocked
        if is_ip_blocked(ip_str):
            raise SSRFProtectionError(
                f"Hostname {hostname} resolves to blocked IP address {ip_str}"
            )
            
        return ip_str
    except socket.gaierror as e:
        logger.error(f"Failed to resolve hostname {hostname}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error resolving hostname {hostname}: {e}")
        raise


async def validate_url_scheme(url: str) -> bool:
    """
    Validate URL scheme
    
    Args:
        url: URL to validate
        
    Returns:
        True if scheme is allowed
        
    Raises:
        URLValidationError: If scheme is not allowed
    """
    parsed = urlparse(url)
    allowed_schemes = settings.ALLOWED_URL_SCHEMES.split(',')
    
    if parsed.scheme not in allowed_schemes:
        raise URLValidationError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed schemes: {', '.join(allowed_schemes)}"
        )
        
    return True


async def check_url_redirects(url: str, max_redirects: int = 5) -> Tuple[str, str]:
    """
    Follow redirects and validate final URL
    
    Args:
        url: Initial URL
        max_redirects: Maximum number of redirects to follow
        
    Returns:
        Tuple of (final_url, final_ip)
        
    Raises:
        URLValidationError: If redirect validation fails
        SSRFProtectionError: If any redirect target is blocked
    """
    if not settings.ENABLE_SSRF_PROTECTION:
        return url, ""
        
    try:
        async with httpx.AsyncClient(follow_redirects=True, max_redirects=max_redirects) as client:
            response = await client.head(url, timeout=10.0)
            final_url = str(response.url)
            
            # Validate final URL
            await validate_url(final_url)
            
            # Get final IP
            parsed = urlparse(final_url)
            final_ip = await resolve_hostname(parsed.hostname)
            
            return final_url, final_ip or ""
            
    except httpx.TooManyRedirects:
        raise URLValidationError(f"Too many redirects (max: {max_redirects})")
    except httpx.RequestError as e:
        logger.warning(f"Error following redirects for {url}: {e}")
        # Continue anyway - the actual scraper will handle connection errors
        return url, ""
    except Exception as e:
        logger.error(f"Unexpected error checking redirects for {url}: {e}")
        raise


async def validate_url(url: str, check_redirects: bool = False) -> Tuple[bool, str]:
    """
    Comprehensive URL validation with SSRF protection
    
    Args:
        url: URL to validate
        check_redirects: Whether to follow and validate redirects
        
    Returns:
        Tuple of (is_valid, resolved_ip)
        
    Raises:
        URLValidationError: If URL format is invalid
        SSRFProtectionError: If URL is blocked for security reasons
    """
    if not url or not isinstance(url, str):
        raise URLValidationError("URL must be a non-empty string")
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise URLValidationError(f"Invalid URL format: {e}")
    
    # Validate scheme
    await validate_url_scheme(url)
    
    # Check if hostname is blocked
    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must have a hostname")
    
    if is_hostname_blocked(hostname):
        raise SSRFProtectionError(f"Hostname '{hostname}' is blocked")
    
    # Check if SSRF protection is enabled
    if not settings.ENABLE_SSRF_PROTECTION:
        logger.warning("SSRF protection is DISABLED - this is unsafe in production!")
        return True, ""
    
    # Resolve hostname and check IP
    resolved_ip = await resolve_hostname(hostname)
    if not resolved_ip:
        raise URLValidationError(f"Could not resolve hostname: {hostname}")
    
    # Check redirects if requested
    if check_redirects:
        final_url, final_ip = await check_url_redirects(url)
        return True, final_ip
    
    return True, resolved_ip


async def validate_and_normalize_url(url: str) -> dict:
    """
    Validate URL and return normalized information
    
    Args:
        url: URL to validate
        
    Returns:
        Dictionary with validation results:
        {
            "original_url": str,
            "is_valid": bool,
            "resolved_ip": str,
            "final_url": str,  # After redirects
            "error": str  # If validation failed
        }
    """
    result = {
        "original_url": url,
        "is_valid": False,
        "resolved_ip": "",
        "final_url": url,
        "error": ""
    }
    
    try:
        # Validate URL
        is_valid, resolved_ip = await validate_url(url, check_redirects=True)
        
        result["is_valid"] = is_valid
        result["resolved_ip"] = resolved_ip
        
    except URLValidationError as e:
        result["error"] = f"URL validation failed: {str(e)}"
        logger.warning(result["error"])
    except SSRFProtectionError as e:
        result["error"] = f"SSRF protection blocked this URL: {str(e)}"
        logger.warning(result["error"])
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        logger.error(result["error"])
    
    return result
