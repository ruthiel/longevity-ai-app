"""
Supabase vector store implementation.
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
import time

from supabase import Client, create_client
from tenacity import retry, stop_after_attempt, wait_exponential

from longevity_ai.config.settings import get_settings
from longevity_ai.core.exceptions import VectorStoreError, SupabaseError
from longevity_ai.core.models import DocumentChunk, RetrievalResult

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """Supabase-based vector store for document embeddings."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get or create Supabase client."""
        if self._client is None:
            self._client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_key
            )
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def store_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """
        Store document chunks with embeddings.
        
        TODO: Verify this matches your Supabase storage logic from notebook
        """
        try:
            logger.info(f"Storing {len(chunks)} chunks to Supabase")
            start_time = time.time()
            
            # Prepare data for insertion
            insert_data = []
            for chunk in chunks:
                data = {
                    "id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "embedding": chunk.embedding,
                    "metadata": chunk.metadata
                }
                insert_data.append(data)
            
            # TODO: Replace with your actual Supabase insertion logic from notebook
            # Insert in batches to handle large datasets
            batch_size = 100
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                
                response = self.client.table(self.settings.supabase_table_name)\
                    .insert(batch).execute()
                
                if not response.data:
                    raise SupabaseError("No data returned from insert operation")
                
                logger.debug(f"Inserted batch {i//batch_size + 1}/{(len(insert_data)-1)//batch_size + 1}")
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully stored {len(chunks)} chunks in {processing_time:.2f}s")
            return True
            
        except Exception as e:
            error_msg = f"Failed to store chunks: {e}"
            logger.error(error_msg)
            raise VectorStoreError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Perform similarity search.
        
        TODO: Replace this with your actual similarity search logic from notebook
        """
        try:
            top_k = top_k or self.settings.default_top_k
            threshold = similarity_threshold or self.settings.similarity_threshold
            
            logger.debug(f"Performing similarity search with top_k={top_k}, threshold={threshold}")
            start_time = time.time()
            
            # TODO: Replace with your actual RPC function call from notebook
            # This assumes you have a match_documents function in Supabase
            rpc_params = {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': top_k
            }
            
            # Add filters if provided
            if filters:
                rpc_params.update(filters)
            
            response = self.client.rpc('match_documents', rpc_params).execute()
            
            if not response.data:
                logger.warning("No similar documents found")
                return []
            
            # Convert to RetrievalResult objects
            results = []
            for item in response.data:
                result = RetrievalResult(
                    chunk_id=item['id'],
                    document_id=item['document_id'],
                    content=item['content'],
                    similarity_score=item['similarity'],
                    source=item.get('source', 'unknown'),
                    source_url=item.get('source_url'),
                    metadata=item.get('metadata', {})
                )
                results.append(result)
            
            processing_time = time.time() - start_time
            logger.info(
                f"Retrieved {len(results)} similar documents in {processing_time:.2f}s "
                f"(avg similarity: {sum(r.similarity_score for r in results)/len(results):.3f})"
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to perform similarity search: {e}"
            logger.error(error_msg)
            raise VectorStoreError(error_msg)
    
    async def delete_chunks(self, chunk_ids: List[str]) -> bool:
        """Delete chunks by IDs."""
        try:
            response = self.client.table(self.settings.supabase_table_name)\
                .delete().in_('id', chunk_ids).execute()
            
            logger.info(f"Deleted {len(chunk_ids)} chunks")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete chunks: {e}"
            logger.error(error_msg)
            raise VectorStoreError(error_msg)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            # Get total count
            count_response = self.client.table(self.settings.supabase_table_name)\
                .select("count", count="exact").execute()
            
            total_chunks = count_response.count if count_response.count else 0
            
            # TODO: Add more statistics from your notebook
            # Examples:
            # - Documents count
            # - Average chunk size
            # - Source distribution
            
            stats = {
                "total_chunks": total_chunks,
                "table_name": self.settings.supabase_table_name,
                "embedding_dimensions": self.settings.embedding_dimensions
            }
            
            logger.info(f"Vector store stats: {stats}")
            return stats
            
        except Exception as e:
            error_msg = f"Failed to get vector store stats: {e}"
            logger.error(error_msg)
            raise VectorStoreError(error_msg)
    
    async def health_check(self) -> bool:
        """Check if the vector store is healthy."""
        try:
            # Simple connectivity test
            response = self.client.table(self.settings.supabase_table_name)\
                .select("count", count="exact").limit(1).execute()
            
            logger.debug("Vector store health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return False


# TODO: Create the Supabase RPC function for similarity search
SUPABASE_RPC_FUNCTION = """
-- Create the match_documents function in your Supabase SQL editor
-- TODO: Customize this based on your actual table structure from notebook

CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5
)
RETURNS TABLE(
  id UUID,
  document_id UUID,
  content TEXT,
  similarity FLOAT,
  source TEXT,
  source_url TEXT,
  metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    longevity_knowledge.id,
    longevity_knowledge.document_id,
    longevity_knowledge.content,
    1 - (longevity_knowledge.embedding <=> query_embedding) AS similarity,
    longevity_knowledge.metadata->>'source' AS source,
    longevity_knowledge.metadata->>'source_url' AS source_url,
    longevity_knowledge.metadata
  FROM longevity_knowledge
  WHERE 1 - (longevity_knowledge.embedding <=> query_embedding) > match_threshold
  ORDER BY longevity_knowledge.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
"""