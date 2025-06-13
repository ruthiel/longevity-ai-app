"""
Pytest configuration and shared fixtures.
"""
import os
import tempfile
from typing import Generator

import pytest

from longevity_ai.config.settings import Settings, get_test_settings


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_settings(temp_dir: str) -> Settings:
    """Create test settings with temporary directories."""
    return get_test_settings(
        data_dir=temp_dir,
        raw_data_dir=os.path.join(temp_dir, "raw"),
        processed_data_dir=os.path.join(temp_dir, "processed"),
        embeddings_dir=os.path.join(temp_dir, "embeddings"),
        openai_api_key="sk-test-key-for-testing-only",
        supabase_url="https://test.supabase.co",
        supabase_key="test-supabase-key",
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response about longevity."
                }
            }
        ],
        "usage": {
            "total_tokens": 50
        }
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "title": "The Science of Longevity",
        "content": "This is a comprehensive guide to living longer and healthier lives through evidence-based practices including exercise, nutrition, sleep optimization, and stress management.",
        "source": "research_paper",
        "author": "Dr. Health Expert",
        "metadata": {
            "journal": "Journal of Longevity Research",
            "year": 2024
        }
    }


@pytest.fixture
def sample_chunk_data():
    """Sample chunk data for testing."""
    return {
        "content": "Exercise is one of the most important factors for longevity. Regular physical activity can extend lifespan by up to 7 years.",
        "chunk_index": 0,
        "start_char": 0,
        "end_char": 110,
        "embedding": [0.1] * 1536,  # Mock embedding
        "metadata": {
            "topic": "exercise",
            "source_section": "introduction"
        }
    }