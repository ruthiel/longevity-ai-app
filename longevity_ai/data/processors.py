"""
Text processing utilities for document chunking and preparation.
"""
import logging
import re
from typing import List, Optional
from uuid import UUID

from langchain.text_splitter import RecursiveCharacterTextSplitter

from longevity_ai.config.settings import get_settings
from longevity_ai.core.exceptions import DataProcessingError
from longevity_ai.core.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text processing and document chunking."""
    
    def __init__(self):
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        TODO: Add your specific text cleaning logic from notebook
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        # TODO: Add your specific cleaning rules from notebook
        # Examples:
        # - Remove special characters
        # - Fix encoding issues
        # - Standardize formatting
        # - Remove unwanted sections
        
        return text
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into chunks for embedding.
        
        TODO: Verify this matches your chunking strategy from notebook
        """
        try:
            logger.debug(f"Chunking document: {document.title}")
            
            # Clean the content first
            cleaned_content = self.clean_text(document.content)
            
            # Split into chunks using Langchain
            text_chunks = self.text_splitter.split_text(cleaned_content)
            
            # Convert to DocumentChunk objects
            chunks = []
            current_pos = 0
            
            for i, chunk_text in enumerate(text_chunks):
                # Find the position of this chunk in the original text
                start_pos = cleaned_content.find(chunk_text, current_pos)
                if start_pos == -1:
                    start_pos = current_pos
                
                end_pos = start_pos + len(chunk_text)
                
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=i,
                    start_char=start_pos,
                    end_char=end_pos,
                    metadata={
                        'document_title': document.title,
                        'document_source': document.source.value,
                        'chunk_length': len(chunk_text),
                        'document_metadata': document.metadata
                    }
                )
                
                chunks.append(chunk)
                current_pos = end_pos
            
            logger.info(f"Created {len(chunks)} chunks from document: {document.title}")
            return chunks
            
        except Exception as e:
            error_msg = f"Failed to chunk document {document.title}: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg)
    
    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for document in documents:
            try:
                chunks = self.chunk_document(document)
                all_chunks.extend(chunks)
                
                # Respect max chunks per document
                if len(chunks) > self.settings.max_chunks_per_doc:
                    logger.warning(
                        f"Document {document.title} has {len(chunks)} chunks, "
                        f"exceeding limit of {self.settings.max_chunks_per_doc}"
                    )
                    # Keep only the first N chunks
                    chunks = chunks[:self.settings.max_chunks_per_doc]
                    all_chunks = all_chunks[:-len(chunks)] + chunks
                
            except Exception as e:
                logger.error(f"Failed to process document {document.title}: {e}")
                continue
        
        logger.info(f"Created {len(all_chunks)} total chunks from {len(documents)} documents")
        return all_chunks
    
    def validate_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Validate and filter chunks."""
        valid_chunks = []
        
        for chunk in chunks:
            if self._is_valid_chunk(chunk):
                valid_chunks.append(chunk)
            else:
                logger.debug(f"Skipping invalid chunk from document {chunk.document_id}")
        
        logger.info(f"Validated {len(valid_chunks)}/{len(chunks)} chunks")
        return valid_chunks
    
    def _is_valid_chunk(self, chunk: DocumentChunk) -> bool:
        """Check if chunk meets validation criteria."""
        # TODO: Add your specific chunk validation from notebook
        
        # Basic validation
        if not chunk.content or len(chunk.content.strip()) < 20:
            return False
        
        # Check for meaningful content (not just whitespace/punctuation)
        meaningful_chars = sum(1 for c in chunk.content if c.isalnum())
        if meaningful_chars < 10:
            return False
        
        return True


# TODO: Add your specific preprocessing logic from notebook
class LongevityTextProcessor(TextProcessor):
    """Specialized text processor for longevity content."""
    
    def clean_text(self, text: str) -> str:
        """Enhanced cleaning for longevity/health content."""
        text = super().clean_text(text)
        
        # TODO: Add domain-specific cleaning from your notebook
        # Examples:
        # - Standardize medical terminology
        # - Remove/fix citation formats
        # - Handle special characters in health data
        # - Normalize measurement units
        
        return text
    
    def extract_key_topics(self, text: str) -> List[str]:
        """
        Extract key longevity topics from text.
        
        TODO: Implement your topic extraction logic from notebook
        """
        topics = []
        
        # Define longevity-related keywords
        longevity_keywords = {
            'exercise': ['exercise', 'workout', 'fitness', 'training', 'physical activity'],
            'nutrition': ['nutrition', 'diet', 'food', 'eating', 'nutrients'],
            'sleep': ['sleep', 'rest', 'circadian', 'insomnia'],
            'stress': ['stress', 'anxiety', 'meditation', 'mindfulness'],
            'supplements': ['supplement', 'vitamin', 'mineral', 'nootropic'],
            'aging': ['aging', 'longevity', 'lifespan', 'healthspan']
        }
        
        text_lower = text.lower()
        
        for topic, keywords in longevity_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics