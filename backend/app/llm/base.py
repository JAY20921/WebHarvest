"""
Base LLM Provider Interface
Abstract class that all LLM providers must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """
    Standardized LLM response
    """
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    Ensures consistent interface across Groq, Gemini, and future providers
    """
    
    def __init__(self, api_key: str, model: str, timeout: int = 45):
        """
        Initialize LLM provider
        
        Args:
            api_key: API key for the provider
            model: Model identifier
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.provider_name = self.__class__.__name__.replace('Provider', '').lower()
    
    @abstractmethod
    async def generate_extraction_schema(
        self,
        user_prompt: str,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate extraction schema from user prompt and page context
        
        Args:
            user_prompt: Natural language extraction instruction
            page_context: Page summary from DOM analyzer
            
        Returns:
            Dictionary with extraction schema:
            {
                'fields': {'field_name': 'type', ...},
                'container_selector': '.product-card',
                'field_selectors': {'field_name': '.selector', ...},
                'filters': [optional filters],
            }
            
        Raises:
            LLMError: If generation fails
        """
        pass
    
    @abstractmethod
    async def analyze_page_structure(
        self,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze page structure and identify data patterns
        
        Args:
            page_context: Page summary from DOM analyzer
            
        Returns:
            Dictionary with structural analysis
            
        Raises:
            LLMError: If analysis fails
        """
        pass
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        General text completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse object
            
        Raises:
            LLMError: If completion fails
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get provider name
        
        Returns:
            Provider name (e.g., 'groq', 'gemini')
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if provider is accessible and healthy
        
        Returns:
            True if healthy, False otherwise
        """
        pass
