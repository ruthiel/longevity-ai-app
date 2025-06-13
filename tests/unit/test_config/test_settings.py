"""
Tests for configuration management.
"""
import os
import pytest

from longevity_ai.config.settings import Settings, get_settings, get_test_settings
from longevity_ai.core.exceptions import ValidationError


class TestSettings:
    """Test settings configuration."""
    
    def test_settings_creation_with_required_fields(self):
        """Test creating settings with all required fields."""
        settings = Settings(
            openai_api_key="sk-test-key",
            supabase_url="https://test.supabase.co",
            supabase_key="test-key"
        )
        
        assert settings.openai_api_key == "sk-test-key"
        assert settings.supabase_url == "https://test.supabase.co"
        assert settings.supabase_key == "test-key"
    
    def test_settings_validation_openai_key(self):
        """Test OpenAI key validation."""
        with pytest.raises(ValueError, match="OpenAI API key must start with"):
            Settings(
                openai_api_key="invalid-key",
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
    
    def test_settings_validation_supabase_url(self):
        """Test Supabase URL validation."""
        with pytest.raises(ValueError, match="Supabase URL must start with"):
            Settings(
                openai_api_key="sk-test-key",
                supabase_url="http://invalid-url",
                supabase_key="test-key"
            )
    
    def test_settings_validation_chunk_overlap(self):
        """Test chunk overlap validation."""
        with pytest.raises(ValueError, match="Chunk overlap must be less than"):
            Settings(
                openai_api_key="sk-test-key",
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
                chunk_size=1000,
                chunk_overlap=1000
            )
    
    def test_settings_properties(self):
        """Test settings properties."""
        settings = Settings(
            openai_api_key="sk-test-key",
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
            environment="development"
        )
        
        assert settings.is_development is True
        assert settings.is_production is False
        assert settings.is_testing is False
    
    def test_get_data_path(self):
        """Test data path generation."""
        settings = Settings(
            openai_api_key="sk-test-key",
            supabase_url="https://test.supabase.co",
            supabase_key="test-key"
        )
        
        raw_path = settings.get_data_path("test.json", "raw")
        assert raw_path == "data/raw/test.json"
        
        processed_path = settings.get_data_path("test.json", "processed")
        assert processed_path == "data/processed/test.json"
    
    def test_get_test_settings(self):
        """Test test settings factory."""
        test_settings = get_test_settings(
            custom_field="test_value"
        )
        
        assert test_settings.environment == "testing"
        assert test_settings.debug is True
        assert test_settings.log_level == "DEBUG"