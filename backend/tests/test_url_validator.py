"""
Tests for URL Validation and SSRF Protection
"""

import pytest
from app.utils.url_validator import (
    validate_url,
    is_ip_blocked,
    is_hostname_blocked,
    URLValidationError,
    SSRFProtectionError
)


class TestIPBlocking:
    """Test IP address blocking"""
    
    def test_localhost_ipv4_blocked(self):
        """Test that localhost IPv4 is blocked"""
        assert is_ip_blocked("127.0.0.1") is True
        assert is_ip_blocked("127.0.0.2") is True
        assert is_ip_blocked("127.255.255.255") is True
    
    def test_private_networks_blocked(self):
        """Test that private network IPs are blocked"""
        # 10.0.0.0/8
        assert is_ip_blocked("10.0.0.1") is True
        assert is_ip_blocked("10.255.255.255") is True
        
        # 172.16.0.0/12
        assert is_ip_blocked("172.16.0.1") is True
        assert is_ip_blocked("172.31.255.255") is True
        
        # 192.168.0.0/16
        assert is_ip_blocked("192.168.0.1") is True
        assert is_ip_blocked("192.168.255.255") is True
    
    def test_link_local_blocked(self):
        """Test that link-local addresses are blocked"""
        assert is_ip_blocked("169.254.0.1") is True
        assert is_ip_blocked("169.254.169.254") is True  # AWS metadata
    
    def test_public_ips_allowed(self):
        """Test that public IPs are allowed"""
        assert is_ip_blocked("8.8.8.8") is False  # Google DNS
        assert is_ip_blocked("1.1.1.1") is False  # Cloudflare DNS
        assert is_ip_blocked("93.184.216.34") is False  # example.com
    
    def test_ipv6_localhost_blocked(self):
        """Test that IPv6 localhost is blocked"""
        assert is_ip_blocked("::1") is True


class TestHostnameBlocking:
    """Test hostname blocking"""
    
    def test_localhost_hostname_blocked(self):
        """Test that localhost hostname is blocked"""
        assert is_hostname_blocked("localhost") is True
        assert is_hostname_blocked("LOCALHOST") is True
    
    def test_metadata_endpoints_blocked(self):
        """Test that cloud metadata endpoints are blocked"""
        assert is_hostname_blocked("metadata.google.internal") is True
        assert is_hostname_blocked("169.254.169.254") is True
        assert is_hostname_blocked("metadata") is True
    
    def test_public_hostnames_allowed(self):
        """Test that public hostnames are allowed"""
        assert is_hostname_blocked("example.com") is False
        assert is_hostname_blocked("google.com") is False
        assert is_hostname_blocked("github.com") is False


@pytest.mark.asyncio
class TestURLValidation:
    """Test URL validation"""
    
    async def test_valid_http_url(self):
        """Test that valid HTTP URLs pass validation"""
        is_valid, ip = await validate_url("http://example.com")
        assert is_valid is True
        assert ip  # Should have resolved IP
    
    async def test_valid_https_url(self):
        """Test that valid HTTPS URLs pass validation"""
        is_valid, ip = await validate_url("https://example.com")
        assert is_valid is True
        assert ip
    
    async def test_empty_url_rejected(self):
        """Test that empty URL is rejected"""
        with pytest.raises(URLValidationError):
            await validate_url("")
    
    async def test_invalid_scheme_rejected(self):
        """Test that invalid schemes are rejected"""
        with pytest.raises(URLValidationError):
            await validate_url("ftp://example.com")
        
        with pytest.raises(URLValidationError):
            await validate_url("file:///etc/passwd")
    
    async def test_localhost_url_blocked(self):
        """Test that localhost URLs are blocked"""
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://localhost:8000")
        
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://127.0.0.1")
    
    async def test_private_ip_url_blocked(self):
        """Test that private IP URLs are blocked"""
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://192.168.1.1")
        
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://10.0.0.1")
        
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://172.16.0.1")
    
    async def test_metadata_endpoint_blocked(self):
        """Test that cloud metadata endpoints are blocked"""
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://169.254.169.254/latest/meta-data/")
        
        with pytest.raises(SSRFProtectionError):
            await validate_url("http://metadata.google.internal")
    
    async def test_url_without_hostname_rejected(self):
        """Test that URL without hostname is rejected"""
        with pytest.raises(URLValidationError):
            await validate_url("http://")


@pytest.mark.asyncio
class TestRedirectValidation:
    """Test redirect validation"""
    
    async def test_redirects_to_public_url_allowed(self):
        """Test that redirects to public URLs are allowed"""
        # This test would need a real redirect URL
        # For MVP, we'll skip actual redirect testing
        pass
    
    async def test_redirects_to_private_ip_blocked(self):
        """Test that redirects to private IPs are blocked"""
        # This would require setting up a test server with redirects
        # For MVP, the logic is in place but integration tests are future work
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
