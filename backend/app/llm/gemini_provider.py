"""
Google Gemini LLM Provider Implementation
Reliable fallback with generous rate limits
"""

import json
import asyncio
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.llm.base import LLMProvider, LLMResponse
from app.llm.prompts import create_extraction_schema_prompt, create_structure_analysis_prompt
from app.core.exceptions import LLMError
import logging

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider
    Reliable fallback with good quality and generous limits
    """
    
    def __init__(self, api_key: str, model: str, timeout: int = 45):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google API key
            model: Model name (e.g., 'gemini-1.5-flash')
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, model, timeout)
        genai.configure(api_key=api_key)
        
        # Configure model with JSON mode hint
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        self.model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
        )
    
    async def generate_extraction_schema(
        self,
        user_prompt: str,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate extraction schema using Gemini"""
        logger.info(f"Gemini: Generating extraction schema for prompt: {user_prompt[:50]}...")
        
        try:
            page_context_str = json.dumps(page_context, indent=2)
            system_prompt, user_message = create_extraction_schema_prompt(
                user_prompt, page_context_str
            )
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_message}"
            
            # Generate content asynchronously
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model_instance.generate_content, full_prompt),
                timeout=self.timeout
            )
            
            # Parse response
            content = response.text
            
            # Extract JSON from response (Gemini might wrap it in markdown)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            schema = json.loads(content)
            
            logger.info("Gemini: Successfully generated extraction schema")
            return schema
            
        except asyncio.TimeoutError:
            logger.error("Gemini: Request timeout")
            raise LLMError("Gemini request timeout")
        
        except json.JSONDecodeError as e:
            logger.error(f"Gemini: Failed to parse JSON response: {e}")
            raise LLMError(f"Invalid JSON response from Gemini: {e}")
        
        except Exception as e:
            logger.error(f"Gemini: Error generating extraction schema: {e}")
            raise LLMError(f"Gemini API error: {str(e)}")
    
    async def analyze_page_structure(
        self,
        page_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze page structure using Gemini"""
        logger.info("Gemini: Analyzing page structure...")
        
        try:
            page_context_str = json.dumps(page_context, indent=2)
            system_prompt, user_message = create_structure_analysis_prompt(
                page_context_str
            )
            
            full_prompt = f"{system_prompt}\n\n{user_message}"
            
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model_instance.generate_content, full_prompt),
                timeout=self.timeout
            )
            
            content = response.text
            
            # Extract JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            analysis = json.loads(content)
            
            logger.info("Gemini: Successfully analyzed page structure")
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini: Error analyzing page structure: {e}")
            raise LLMError(f"Gemini API error: {str(e)}")
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """General completion using Gemini"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model_instance.generate_content, full_prompt),
                timeout=self.timeout
            )
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider="gemini",
                tokens_used=None,  # Gemini doesn't provide token counts easily
                finish_reason="stop",
            )
            
        except Exception as e:
            logger.error(f"Gemini: Error in completion: {e}")
            raise LLMError(f"Gemini API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "gemini"
    
    async def check_health(self) -> bool:
        """Check Gemini API health"""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model_instance.generate_content,
                    "Hello"
                ),
                timeout=10
            )
            return response is not None
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False
