"""
LLM Provider Factory
Creates provider instances based on configuration
"""

from typing import Optional
from app.llm.base import LLMProvider
from app.llm.groq_provider import GroqProvider
from app.llm.gemini_provider import GeminiProvider
from app.core.config import settings
from app.core.exceptions import LLMError
import logging

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances
    """
    
    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMProvider:
        """
        Create LLM provider instance
        
        Args:
            provider_name: Name of provider ('groq' or 'gemini')
            api_key: Optional API key (uses settings if not provided)
            model: Optional model name (uses settings if not provided)
            
        Returns:
            LLMProvider instance
            
        Raises:
            LLMError: If provider creation fails
        """
        provider_name = provider_name.lower()
        
        if provider_name == "groq":
            api_key = api_key or settings.GROQ_API_KEY
            model = model or settings.GROQ_MODEL
            
            if not api_key:
                raise LLMError("Groq API key not configured")
            
            logger.info(f"Creating Groq provider with model: {model}")
            return GroqProvider(
                api_key=api_key,
                model=model,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
        
        elif provider_name == "gemini":
            api_key = api_key or settings.GEMINI_API_KEY
            model = model or settings.GEMINI_MODEL
            
            if not api_key:
                raise LLMError("Gemini API key not configured")
            
            logger.info(f"Creating Gemini provider with model: {model}")
            return GeminiProvider(
                api_key=api_key,
                model=model,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
        
        else:
            raise LLMError(f"Unknown LLM provider: {provider_name}")
    
    @staticmethod
    def create_primary_provider() -> LLMProvider:
        """
        Create primary provider from settings
        
        Returns:
            Primary LLMProvider instance
        """
        return LLMProviderFactory.create_provider(settings.LLM_PRIMARY_PROVIDER)
    
    @staticmethod
    def create_fallback_provider() -> Optional[LLMProvider]:
        """
        Create fallback provider from settings
        
        Returns:
            Fallback LLMProvider instance or None if disabled
        """
        if not settings.LLM_FALLBACK_ENABLED:
            logger.info("LLM fallback is disabled")
            return None
        
        try:
            return LLMProviderFactory.create_provider(settings.LLM_FALLBACK_PROVIDER)
        except LLMError as e:
            logger.warning(f"Failed to create fallback provider: {e}")
            return None
