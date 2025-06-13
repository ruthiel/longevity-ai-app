"""
Data loading utilities for the Longevity AI application.
Handles loading from various sources: JSON, web scraping, PDFs, etc.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4

from longevity_ai.config.settings import get_settings
from longevity_ai.core.exceptions import DataProcessingError
from longevity_ai.core.models import Document, DocumentSource

logger = logging.getLogger(__name__)


class JSONDataLoader:
    """Loads documents from JSON files."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def load_from_file(self, file_path: str) -> List[Document]:
        """
        Load documents from a JSON file.
        
        TODO: Replace this with your actual JSON loading logic from notebook
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of Document objects
        """
        try:
            logger.info(f"Loading documents from {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            # TODO: Replace this section with your actual JSON structure parsing
            # This is a template - adapt to your actual JSON format
            if isinstance(data, list):
                for item in data:
                    doc = self._parse_document_item(item)
                    if doc:
                        documents.append(doc)
            elif isinstance(data, dict):
                # If it's a single document or has a specific structure
                doc = self._parse_document_item(data)
                if doc:
                    documents.append(doc)
            
            logger.info(f"Successfully loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            error_msg = f"Failed to load documents from {file_path}: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg)
    
    def _parse_document_item(self, item: Dict[str, Any]) -> Optional[Document]:
        """
        Parse a single document item from JSON.
        
        TODO: Customize this method based on your JSON structure
        
        Expected JSON format (adapt as needed):
        {
            "title": "Document Title",
            "content": "Document content...",
            "source": "research_paper",
            "url": "https://example.com",
            "author": "Author Name",
            "metadata": {...}
        }
        """
        try:
            # Basic required fields
            content = item.get('content', '').strip()
            if not content:
                logger.warning("Skipping document with empty content")
                return None
            
            # Create document with available fields
            doc = Document(
                title=item.get('title', 'Untitled Document'),
                content=content,
                source=self._map_source_type(item.get('source', 'unknown')),
                source_url=item.get('url') or item.get('source_url'),
                author=item.get('author'),
                metadata=item.get('metadata', {})
            )
            
            # Add any additional metadata from the JSON
            for key, value in item.items():
                if key not in ['title', 'content', 'source', 'url', 'source_url', 'author', 'metadata']:
                    doc.metadata[key] = value
            
            return doc
            
        except Exception as e:
            logger.warning(f"Failed to parse document item: {e}")
            return None
    
    def _map_source_type(self, source_str: str) -> DocumentSource:
        """Map string source to DocumentSource enum."""
        source_mapping = {
            'research_paper': DocumentSource.RESEARCH_PAPER,
            'research': DocumentSource.RESEARCH_PAPER,
            'paper': DocumentSource.RESEARCH_PAPER,
            'podcast': DocumentSource.PODCAST_TRANSCRIPT,
            'podcast_transcript': DocumentSource.PODCAST_TRANSCRIPT,
            'book': DocumentSource.BOOK_EXCERPT,
            'book_excerpt': DocumentSource.BOOK_EXCERPT,
            'website': DocumentSource.WEBSITE_CONTENT,
            'web': DocumentSource.WEBSITE_CONTENT,
            'blog': DocumentSource.BLOG_POST,
            'blog_post': DocumentSource.BLOG_POST,
            'news': DocumentSource.NEWS_ARTICLE,
            'article': DocumentSource.NEWS_ARTICLE,
        }
        
        return source_mapping.get(source_str.lower(), DocumentSource.UNKNOWN)


class DataProcessor:
    """Processes loaded documents for the RAG pipeline."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_documents(self, documents: List[Document]) -> List[Document]:
        """
        Validate and filter documents.
        
        TODO: Add your specific validation logic from notebook
        """
        valid_documents = []
        
        for doc in documents:
            if self._is_valid_document(doc):
                valid_documents.append(doc)
            else:
                logger.warning(f"Skipping invalid document: {doc.title}")
        
        logger.info(f"Validated {len(valid_documents)}/{len(documents)} documents")
        return valid_documents
    
    def _is_valid_document(self, doc: Document) -> bool:
        """Check if document meets validation criteria."""
        # Basic validation
        if not doc.content or len(doc.content.strip()) < 50:
            return False
        
        # TODO: Add your specific validation rules from notebook
        # Examples:
        # - Minimum content length
        # - Required keywords
        # - Source type filtering
        # - Content quality checks
        
        return True
    
    def enrich_metadata(self, documents: List[Document]) -> List[Document]:
        """
        Enrich documents with additional metadata.
        
        TODO: Add your metadata enrichment logic from notebook
        """
        for doc in documents:
            # Add processing timestamp
            doc.metadata['processed_at'] = doc.created_at.isoformat()
            
            # Add content statistics
            doc.metadata['content_length'] = len(doc.content)
            doc.metadata['word_count'] = len(doc.content.split())
            
            # TODO: Add your specific enrichment logic
            # Examples:
            # - Extract keywords
            # - Categorize content
            # - Add topic tags
            # - Calculate readability scores
        
        logger.info(f"Enriched metadata for {len(documents)} documents")
        return documents


# TODO: Replace this with your actual data loading workflow
class LongevityDataLoader:
    """Main data loader orchestrating the full pipeline."""
    
    def __init__(self):
        self.json_loader = JSONDataLoader()
        self.processor = DataProcessor()
        self.settings = get_settings()
    
    def load_knowledge_base(self, data_sources: List[str] = None) -> List[Document]:
        """
        Load complete knowledge base from configured sources.
        
        TODO: Customize this to match your data loading workflow from notebook
        
        Args:
            data_sources: List of file paths or URLs to load from
            
        Returns:
            List of processed Document objects
        """
        if data_sources is None:
            # TODO: Set your default data sources
            data_sources = [
                self.settings.get_data_path("longevity_research.json", "raw"),
                self.settings.get_data_path("podcast_transcripts.json", "raw"),
                # Add your other data sources here
            ]
        
        all_documents = []
        
        for source in data_sources:
            try:
                logger.info(f"Processing data source: {source}")
                
                if source.endswith('.json'):
                    docs = self.json_loader.load_from_file(source)
                    all_documents.extend(docs)
                
                # TODO: Add other source types as needed
                # elif source.endswith('.pdf'):
                #     docs = self.pdf_loader.load_from_file(source)
                # elif source.startswith('http'):
                #     docs = self.web_loader.load_from_url(source)
                
            except Exception as e:
                logger.error(f"Failed to load from {source}: {e}")
                continue
        
        logger.info(f"Loaded {len(all_documents)} documents from {len(data_sources)} sources")
        
        # Process and validate
        valid_documents = self.processor.validate_documents(all_documents)
        enriched_documents = self.processor.enrich_metadata(valid_documents)
        
        # Ensure data directories exist
        self.settings.ensure_data_directories()
        
        # TODO: Optionally save processed documents
        # self._save_processed_documents(enriched_documents)
        
        return enriched_documents
    
    def _save_processed_documents(self, documents: List[Document]) -> str:
        """Save processed documents for caching."""
        output_path = self.settings.get_data_path("processed_documents.json", "processed")
        
        # Convert to serializable format
        doc_data = [
            {
                "id": str(doc.id),
                "title": doc.title,
                "content": doc.content,
                "source": doc.source.value,
                "source_url": doc.source_url,
                "author": doc.author,
                "metadata": doc.metadata,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(documents)} processed documents to {output_path}")
        return output_path