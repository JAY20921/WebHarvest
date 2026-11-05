"""
Groq LLM Provider Implementation
Fast inference with Mixtral and Llama models
"""

import json
import asyncio
from typing import Dict, Any, Optional
from groq import AsyncGroq
from app.llm.base import LLMProvider, LLMResponse
from app.llm.prompts import create_extraction_schema_prompt, create_structure_analysis_prompt
from app.core.exceptions import LLMError
import logging

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Groq Cloud API provider
    Supports Mixtral and Llama models with fast inference
    """
    
    def __init__(self, api_key: str, model: str, timeout: int = 45):
        """
        Initialize Groq provider
        
        Args:
            api_key: Groq API key
            model: Model name (e.g., 'mixtral-8x7b-32768')
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, model, timeout)
        self.client = AsyncGroq(api_key=api_key, timeout=timeout)
    
    async def generate_extraction_schema(
        self,
        user_prompt: str,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate extraction schema using Groq"""
        logger.info(f"Groq: Generating extraction schema for prompt: {user_prompt[:50]}...")
        
        try:
            # Create prompt
            page_context_str = json.dumps(page_context, indent=2)
            system_prompt, user_message = create_extraction_schema_prompt(
                user_prompt, page_context_str
            )
            
            # Call Groq API with JSON mode
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_tokens=1500,
                response_format={"type": "json_object"},  # Force JSON output
            )
            
            # Parse response
            content = response.choices[0].message.content
            schema = json.loads(content)
            
            logger.info(f"Groq: Successfully generated extraction schema")
            return schema
            
        except json.JSONDecodeError as e:
            logger.error(f"Groq: Failed to parse JSON response: {e}")
            raise LLMError(f"Invalid JSON response from Groq: {e}")
        
        except Exception as e:
            logger.error(f"Groq: Error generating extraction schema: {e}")
            raise LLMError(f"Groq API error: {str(e)}")
    
    async def analyze_page_structure(
        self,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze page structure using Groq"""
        logger.info("Groq: Analyzing page structure...")
        
        try:
            page_context_str = json.dumps(page_context, indent=2)
            system_prompt, user_message = create_structure_analysis_prompt(
                page_context_str
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            logger.info("Groq: Successfully analyzed page structure")
            return analysis
            
        except Exception as e:
            logger.error(f"Groq: Error analyzing page structure: {e}")
            raise LLMError(f"Groq API error: {str(e)}")
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """General completion using Groq"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 1500,
            )
            
            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content,
                model=self.model,
                provider="groq",
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=choice.finish_reason,
            )
            
        except Exception as e:
            logger.error(f"Groq: Error in completion: {e}")
            raise LLMError(f"Groq API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "groq"
    
    async def check_health(self) -> bool:
        """Check Groq API health"""
        try:
            # Simple test completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            return response is not None
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")
            return False
