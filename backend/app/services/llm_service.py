"""
LLM Service - High-level orchestration of LLM operations
"""

from typing import Dict, Any, Tuple
from app.llm.fallback_manager import fallback_manager
from app.scrapers.dom_analyzer import DOMAnalyzer
from app.core.exceptions import LLMError
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    High-level service for LLM operations
    Orchestrates DOM analysis, schema generation, and validation
    """
    
    def __init__(self):
        """Initialize LLM service"""
        self.fallback_manager = fallback_manager
    
    async def generate_extraction_schema_from_page(
        self,
        user_prompt: str,
        html: str,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Generate extraction schema from user prompt and HTML
        
        Args:
            user_prompt: Natural language extraction instruction
            html: Raw HTML content
            
        Returns:
            Tuple of (schema, provider_name)
            {
                'fields': {'field_name': 'type', ...},
                'container_selector': '.product-card',
                'field_selectors': {'field_name': '.selector', ...},
            }
            
        Raises:
            LLMError: If schema generation fails
        """
        logger.info(f"Generating extraction schema for prompt: {user_prompt[:100]}...")
        
        try:
            # Analyze DOM
            analyzer = DOMAnalyzer(html)
            page_summary = analyzer.create_summary()
            
            # Generate schema using LLM with fallback
            schema, provider = await self.fallback_manager.generate_extraction_schema(
                user_prompt=user_prompt,
                page_context=page_summary,
            )
            
            # Validate schema structure
            self._validate_schema_structure(schema)
            
            logger.info(f"Successfully generated extraction schema using {provider}")
            return schema, provider
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate extraction schema: {e}")
            raise LLMError(f"Schema generation failed: {str(e)}")
    
    async def analyze_page_structure(
        self,
        html: str,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Analyze page structure using LLM
        
        Args:
            html: Raw HTML content
            
        Returns:
            Tuple of (analysis, provider_name)
            
        Raises:
            LLMError: If analysis fails
        """
        logger.info("Analyzing page structure with LLM...")
        
        try:
            # Analyze DOM
            analyzer = DOMAnalyzer(html)
            page_summary = analyzer.create_summary()
            
            # Get LLM analysis with fallback
            analysis, provider = await self.fallback_manager.analyze_page_structure(
                page_context=page_summary,
            )
            
            logger.info(f"Successfully analyzed page structure using {provider}")
            return analysis, provider
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Failed to analyze page structure: {e}")
            raise LLMError(f"Structure analysis failed: {str(e)}")
    
    async def check_llm_health(self) -> Dict[str, Any]:
        """
        Check health of LLM providers
        
        Returns:
            Dictionary with health status
        """
        try:
            provider_health = await self.fallback_manager.check_providers_health()
            
            all_healthy = all(provider_health.values())
            any_healthy = any(provider_health.values())
            
            return {
                'status': 'healthy' if all_healthy else ('degraded' if any_healthy else 'unhealthy'),
                'providers': provider_health,
                'fallback_available': len([h for h in provider_health.values() if h]) > 1,
            }
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {
                'status': 'unhealthy',
                'providers': {},
                'fallback_available': False,
                'error': str(e),
            }
    
    def _validate_schema_structure(self, schema: Dict[str, Any]):
        """
        Validate that LLM-generated schema has required structure
        
        Args:
            schema: Schema to validate
            
        Raises:
            LLMError: If schema is invalid
        """
        required_keys = ['fields', 'container_selector', 'field_selectors']
        
        for key in required_keys:
            if key not in schema:
                raise LLMError(f"Generated schema missing required key: {key}")
        
        if not isinstance(schema['fields'], dict):
            raise LLMError("Schema 'fields' must be a dictionary")
        
        if not isinstance(schema['field_selectors'], dict):
            raise LLMError("Schema 'field_selectors' must be a dictionary")
        
        if not schema['container_selector']:
            raise LLMError("Schema 'container_selector' cannot be empty")
        
        if not schema['fields']:
            raise LLMError("Schema 'fields' cannot be empty")


# Create singleton instance
llm_service = LLMService()
