"""
LLM Fallback Manager
Handles automatic failover between LLM providers
"""

import asyncio
from typing import Dict, Any, Optional, Callable, TypeVar, Awaitable
from app.llm.base import LLMProvider, LLMResponse
from app.llm.provider_factory import LLMProviderFactory
from app.core.config import settings
from app.core.exceptions import LLMError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class FallbackManager:
    """
    Manages automatic fallback between LLM providers
    Tries primary provider first, falls back to secondary on failure
    """
    
    def __init__(self):
        """Initialize fallback manager"""
        self._primary_provider: Optional[LLMProvider] = None
        self._fallback_provider: Optional[LLMProvider] = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Lazy initialization of providers"""
        if self._initialized:
            return
        
        logger.info("Initializing LLM providers...")
        
        # Create primary provider
        try:
            self._primary_provider = LLMProviderFactory.create_primary_provider()
            logger.info(f"Primary provider: {self._primary_provider.get_provider_name()}")
        except LLMError as e:
            logger.error(f"Failed to initialize primary provider: {e}")
            raise
        
        # Create fallback provider
        try:
            self._fallback_provider = LLMProviderFactory.create_fallback_provider()
            if self._fallback_provider:
                logger.info(f"Fallback provider: {self._fallback_provider.get_provider_name()}")
            else:
                logger.warning("No fallback provider configured")
        except Exception as e:
            logger.warning(f"Failed to initialize fallback provider: {e}")
            self._fallback_provider = None
        
        self._initialized = True
    
    async def execute_with_fallback(
        self,
        operation: Callable[[LLMProvider], Awaitable[T]],
        operation_name: str = "LLM operation",
    ) -> tuple[T, str]:
        """
        Execute operation with automatic fallback
        
        Args:
            operation: Async function that takes LLMProvider and returns result
            operation_name: Name of operation for logging
            
        Returns:
            Tuple of (result, provider_name)
            
        Raises:
            LLMError: If all providers fail
        """
        await self._ensure_initialized()
        
        # Try primary provider
        if self._primary_provider:
            try:
                logger.info(f"{operation_name}: Trying primary provider ({self._primary_provider.get_provider_name()})...")
                result = await self._execute_with_retry(
                    operation,
                    self._primary_provider,
                    max_retries=settings.LLM_MAX_RETRIES,
                )
                logger.info(f"{operation_name}: Success with primary provider")
                return result, self._primary_provider.get_provider_name()
            
            except LLMError as e:
                logger.warning(
                    f"{operation_name}: Primary provider failed: {e}. "
                    f"Attempting fallback..."
                )
        
        # Try fallback provider
        if self._fallback_provider:
            try:
                logger.info(f"{operation_name}: Trying fallback provider ({self._fallback_provider.get_provider_name()})...")
                result = await self._execute_with_retry(
                    operation,
                    self._fallback_provider,
                    max_retries=1,  # Only 1 retry for fallback
                )
                logger.info(f"{operation_name}: Success with fallback provider")
                return result, self._fallback_provider.get_provider_name()
            
            except LLMError as e:
                logger.error(f"{operation_name}: Fallback provider also failed: {e}")
        
        # Both providers failed
        raise LLMError(f"{operation_name}: All LLM providers failed")
    
    async def _execute_with_retry(
        self,
        operation: Callable[[LLMProvider], Awaitable[T]],
        provider: LLMProvider,
        max_retries: int = 2,
    ) -> T:
        """
        Execute operation with exponential backoff retry
        
        Args:
            operation: Operation to execute
            provider: Provider to use
            max_retries: Maximum number of retries
            
        Returns:
            Operation result
            
        Raises:
            LLMError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation(provider)
            
            except LLMError as e:
                last_error = e
                
                # Check if we should retry
                if attempt < max_retries:
                    # Check for rate limit or timeout errors
                    error_str = str(e).lower()
                    should_retry = any(
                        keyword in error_str
                        for keyword in ['rate limit', 'timeout', 'temporary', '429', '503']
                    )
                    
                    if should_retry:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                
                # Don't retry, raise immediately
                raise
        
        # All retries exhausted
        raise last_error
    
    async def generate_extraction_schema(
        self,
        user_prompt: str,
        page_context: Dict[str, Any],
    ) -> tuple[Dict[str, Any], str]:
        """
        Generate extraction schema with fallback
        
        Returns:
            Tuple of (schema, provider_name)
        """
        async def operation(provider: LLMProvider):
            return await provider.generate_extraction_schema(user_prompt, page_context)
        
        return await self.execute_with_fallback(
            operation,
            "Generate extraction schema",
        )
    
    async def analyze_page_structure(
        self,
        page_context: Dict[str, Any],
    ) -> tuple[Dict[str, Any], str]:
        """
        Analyze page structure with fallback
        
        Returns:
            Tuple of (analysis, provider_name)
        """
        async def operation(provider: LLMProvider):
            return await provider.analyze_page_structure(page_context)
        
        return await self.execute_with_fallback(
            operation,
            "Analyze page structure",
        )
    
    async def check_providers_health(self) -> Dict[str, bool]:
        """
        Check health of all providers
        
        Returns:
            Dictionary mapping provider names to health status
        """
        await self._ensure_initialized()
        
        health = {}
        
        if self._primary_provider:
            try:
                health[self._primary_provider.get_provider_name()] = \
                    await self._primary_provider.check_health()
            except Exception:
                health[self._primary_provider.get_provider_name()] = False
        
        if self._fallback_provider:
            try:
                health[self._fallback_provider.get_provider_name()] = \
                    await self._fallback_provider.check_health()
            except Exception:
                health[self._fallback_provider.get_provider_name()] = False
        
        return health


# Create singleton instance
fallback_manager = FallbackManager()
