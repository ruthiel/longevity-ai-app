"""
Embedding generation utilities using OpenAI.
"""
import asyncio
import logging
from typing import List, Optional
import time

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from longevity_ai.config.settings import get_settings
from longevity_ai.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using OpenAI's embedding models."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        TODO: Verify this matches your embedding generation from notebook
        """
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            start_time = time.time()
            
            # TODO: Replace with your actual embedding logic from notebook
            response = await self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            processing_time = time.time() - start_time
            logger.info(
                f"Generated {len(embeddings)} embeddings in {processing_time:.2f}s "
                f"using {response.usage.total_tokens} tokens"
            )
            
            return embeddings
            
        except Exception as e:
            error_msg = f"Failed to generate embeddings: {e}"
            logger.error(error_msg)
            raise EmbeddingError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        TODO: Verify this matches your query embedding from notebook
        """
        try:
            logger.debug(f"Generating query embedding for: {query[:50]}...")
            
            response = await self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=[query]
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated query embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            error_msg = f"Failed to generate query embedding: {e}"
            logger.error(error_msg)
            raise EmbeddingError(error_msg)
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings in batches to handle large datasets."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            batch_embeddings = await self.generate_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
            
            # Add small delay to respect rate limits
            if i + batch_size < len(texts):
                await asyncio.sleep(1)
        
        logger.info(f"Generated {len(all_embeddings)} total embeddings")
        return all_embeddings