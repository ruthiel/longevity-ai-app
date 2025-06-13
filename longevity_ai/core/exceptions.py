"""
Custom exceptions for the Longevity AI application.
Provides structured error handling with proper error codes and messages.
"""
from typing import Any, Dict, Optional


class LongevityAIException(Exception):
    """Base exception for all Longevity AI application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(LongevityAIException):
    """Raised when there's a configuration error."""
    pass


class DatabaseError(LongevityAIException):
    """Raised when there's a database operation error."""
    pass


class VectorStoreError(DatabaseError):
    """Raised when there's a vector store specific error."""
    pass


class EmbeddingError(LongevityAIException):
    """Raised when there's an error generating embeddings."""
    pass


class LLMError(LongevityAIException):
    """Raised when there's an error with LLM operations."""
    pass


class RetrievalError(LongevityAIException):
    """Raised when there's an error during document retrieval."""
    pass


class DataProcessingError(LongevityAIException):
    """Raised when there's an error processing data."""
    pass


class ValidationError(LongevityAIException):
    """Raised when there's a data validation error."""
    pass


class AuthenticationError(LongevityAIException):
    """Raised when there's an authentication error."""
    pass


class RateLimitError(LongevityAIException):
    """Raised when rate limits are exceeded."""
    pass


class ServiceUnavailableError(LongevityAIException):
    """Raised when external services are unavailable."""
    pass


# Specific error subtypes for better error handling

class OpenAIError(LLMError):
    """OpenAI API specific errors."""
    pass


class SupabaseError(DatabaseError):
    """Supabase specific errors."""
    pass


class DocumentNotFoundError(RetrievalError):
    """Raised when requested documents are not found."""
    pass


class InvalidQueryError(ValidationError):
    """Raised when query is invalid or malformed."""
    pass


class ContextTooLongError(LLMError):
    """Raised when context exceeds maximum length."""
    pass