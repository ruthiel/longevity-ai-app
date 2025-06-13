"""
Longevity AI - AI-Powered Longevity Knowledge Assistant

A production-ready application for providing evidence-based longevity advice
using Retrieval Augmented Generation (RAG) with OpenAI and Supabase.
"""

__version__ = "0.1.0"
__author__ = "Ruthiel Trevisan"
__description__ = "AI-Powered Longevity Knowledge Assistant"

# Import main components for easy access
from longevity_ai.config.settings import get_settings
from longevity_ai.config.logging import setup_logging, get_logger
from longevity_ai.core.exceptions import LongevityAIException
from longevity_ai.core.models import (
    Document,
    DocumentChunk,
    ChatMessage,
    ChatSession,
    RetrievalResult,
    RAGResponse,
    HealthCheck
)

# Configure logging when package is imported
import os
if not os.getenv("LONGEVITY_AI_NO_AUTO_LOGGING"):
    try:
        setup_logging()
    except Exception:
        # Silently fail if logging setup fails during import
        pass

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "get_settings",
    "setup_logging",
    "get_logger",
    "LongevityAIException",
    "Document",
    "DocumentChunk", 
    "ChatMessage",
    "ChatSession",
    "RetrievalResult",
    "RAGResponse",
    "HealthCheck",
]