"""
Core data models for the Longevity AI application.
Defines the structure of data objects used throughout the application.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class DocumentSource(str, Enum):
    """Enumeration of document sources."""
    RESEARCH_PAPER = "research_paper"
    PODCAST_TRANSCRIPT = "podcast_transcript"
    BOOK_EXCERPT = "book_excerpt"
    WEBSITE_CONTENT = "website_content"
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    """Enumeration of message roles in conversations."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Document(BaseModel):
    """Represents a document in the knowledge base."""
    
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Document title", max_length=500)
    content: str = Field(..., description="Document content", min_length=1)
    source: DocumentSource = Field(default=DocumentSource.UNKNOWN)
    source_url: Optional[str] = Field(None, description="Original source URL")
    author: Optional[str] = Field(None, description="Document author")
    published_date: Optional[datetime] = Field(None, description="Publication date")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('content')
    def validate_content_length(cls, v):
        """Ensure content is not too long."""
        if len(v) > 100000:  # 100KB limit
            raise ValueError("Document content too long (max 100KB)")
        return v
    
    @validator('source_url')
    def validate_source_url(cls, v):
        """Basic URL validation."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("Source URL must start with http:// or https://")
        return v


class DocumentChunk(BaseModel):
    """Represents a chunk of a document."""
    
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content", min_length=1)
    chunk_index: int = Field(..., description="Index of chunk in document", ge=0)
    start_char: int = Field(..., description="Start character position", ge=0)
    end_char: int = Field(..., description="End character position", ge=0)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('end_char')
    def validate_char_positions(cls, v, values):
        """Ensure end_char is greater than start_char."""
        if 'start_char' in values and v <= values['start_char']:
            raise ValueError("end_char must be greater than start_char")
        return v
    
    @validator('embedding')
    def validate_embedding_dimension(cls, v):
        """Validate embedding dimensions."""
        if v is not None:
            if not isinstance(v, list) or not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("Embedding must be a list of numbers")
            if len(v) not in [1536, 3072]:  # Common OpenAI embedding dimensions
                raise ValueError("Invalid embedding dimension")
        return v


class ChatMessage(BaseModel):
    """Represents a chat message."""
    
    id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="Message content", min_length=1, max_length=10000)
    role: MessageRole = Field(..., description="Message role")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validate message content based on role."""
        if 'role' in values:
            if values['role'] == MessageRole.USER and len(v.strip()) == 0:
                raise ValueError("User message cannot be empty")
        return v.strip()


class ChatSession(BaseModel):
    """Represents a chat session."""
    
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = Field(None, description="User identifier")
    messages: List[ChatMessage] = Field(default_factory=list)
    title: Optional[str] = Field(None, description="Session title", max_length=200)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_message(self, content: str, role: MessageRole, **metadata) -> ChatMessage:
        """Add a message to the session."""
        message = ChatMessage(
            content=content,
            role=role,
            metadata=metadata
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message
    
    @property
    def message_count(self) -> int:
        """Get the number of messages in the session."""
        return len(self.messages)
    
    @property
    def last_message(self) -> Optional[ChatMessage]:
        """Get the last message in the session."""
        return self.messages[-1] if self.messages else None


class RetrievalResult(BaseModel):
    """Represents a document retrieval result."""
    
    chunk_id: UUID = Field(..., description="Chunk ID")
    document_id: UUID = Field(..., description="Parent document ID")
    content: str = Field(..., description="Retrieved content")
    similarity_score: float = Field(..., description="Similarity score", ge=0.0, le=1.0)
    source: DocumentSource = Field(..., description="Document source type")
    source_url: Optional[str] = Field(None, description="Source URL")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_highly_relevant(self) -> bool:
        """Check if the result is highly relevant (>= 0.8 similarity)."""
        return self.similarity_score >= 0.8
    
    @property
    def truncated_content(self) -> str:
        """Get truncated content for display (max 200 chars)."""
        if len(self.content) <= 200:
            return self.content
        return self.content[:197] + "..."


class RAGResponse(BaseModel):
    """Represents a RAG system response."""
    
    id: UUID = Field(default_factory=uuid4)
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="Generated response")
    retrieved_chunks: List[RetrievalResult] = Field(default_factory=list)
    model_used: str = Field(..., description="LLM model used")
    processing_time: float = Field(..., description="Processing time in seconds", ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def avg_similarity_score(self) -> float:
        """Calculate average similarity score of retrieved chunks."""
        if not self.retrieved_chunks:
            return 0.0
        return sum(chunk.similarity_score for chunk in self.retrieved_chunks) / len(self.retrieved_chunks)
    
    @property
    def sources_summary(self) -> Dict[str, int]:
        """Get summary of sources used."""
        sources = {}
        for chunk in self.retrieved_chunks:
            source = chunk.source.value
            sources[source] = sources.get(source, 0) + 1
        return sources


class HealthCheck(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return self.status == "healthy"


class DataIngestionStatus(BaseModel):
    """Status of data ingestion process."""
    
    id: UUID = Field(default_factory=uuid4)
    total_documents: int = Field(..., ge=0)
    processed_documents: int = Field(..., ge=0)
    failed_documents: int = Field(..., ge=0)
    total_chunks: int = Field(..., ge=0)
    processing_time: float = Field(..., ge=0.0)
    status: str = Field(..., description="Processing status")
    errors: List[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate processing progress percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.processed_documents + self.failed_documents) / self.total_documents * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if ingestion is complete."""
        return self.completed_at is not None