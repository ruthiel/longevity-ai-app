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

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "get_settings",
]
