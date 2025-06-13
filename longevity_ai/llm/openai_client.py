"""
OpenAI client for language model operations.
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
import time

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from longevity_ai.config.settings import get_settings
from longevity_ai.core.exceptions import LLMError, OpenAIError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI language model operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate response using OpenAI LLM.
        
        TODO: Verify this matches your LLM generation logic from notebook
        """
        try:
            model = model or self.settings.openai_model
            max_tokens = max_tokens or self.settings.openai_max_tokens
            temperature = temperature or self.settings.openai_temperature
            
            logger.debug(f"Generating response with {model}")
            start_time = time.time()
            
            # TODO: Replace with your actual OpenAI API call from notebook
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            generated_text = response.choices[0].message.content
            
            processing_time = time.time() - start_time
            logger.info(
                f"Generated response in {processing_time:.2f}s "
                f"using {response.usage.total_tokens} tokens"
            )
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Failed to generate LLM response: {e}"
            logger.error(error_msg)
            raise OpenAIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response using chat format.
        
        TODO: Adapt this to your chat logic from notebook if different
        """
        try:
            model = model or self.settings.openai_model
            
            logger.debug(f"Generating chat response with {len(messages)} messages")
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature,
                **kwargs
            )
            
            generated_text = response.choices[0].message.content
            
            processing_time = time.time() - start_time
            logger.info(f"Generated chat response in {processing_time:.2f}s")
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Failed to generate chat response: {e}"
            logger.error(error_msg)
            raise OpenAIError(error_msg)
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            # Simple test call
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            logger.debug("OpenAI health check passed")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False