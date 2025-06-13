#!/usr/bin/env python3
"""
Test script to verify configuration setup.
"""
import os
import sys
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from longevity_ai.config.settings import get_test_settings
from longevity_ai.config.logging import setup_logging, get_logger
from longevity_ai.core.models import Document, DocumentChunk, ChatMessage
from longevity_ai.core.exceptions import ConfigurationError


def test_configuration():
    """Test the configuration system."""
    print("🧪 Testing Longevity AI Configuration...")
    
    # Test settings
    print("\n📋 Testing Settings...")
    try:
        settings = get_test_settings()
        print(f"✅ Settings loaded: {settings.app_name} v{settings.app_version}")
        print(f"✅ Environment: {settings.environment}")
        print(f"✅ Data directories: {settings.data_dir}")
        
        # Test data path generation
        test_path = settings.get_data_path("test.json", "processed")
        print(f"✅ Data path generation: {test_path}")
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False
    
    # Test logging
    print("\n📝 Testing Logging...")
    try:
        setup_logging(level="INFO", format_type="console")
        logger = get_logger(__name__)
        logger.info("Test log message")
        print("✅ Logging configured successfully")
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False
    
    # Test models
    print("\n📊 Testing Data Models...")
    try:
        # Test Document model
        doc = Document(
            title="Test Document",
            content="This is a test document about longevity research.",
            source="research_paper"
        )
        print(f"✅ Document model: {doc.title}")
        
        # Test DocumentChunk model
        chunk = DocumentChunk(
            document_id=doc.id,
            content="This is a test chunk.",
            chunk_index=0,
            start_char=0,
            end_char=20
        )
        print(f"✅ DocumentChunk model: {len(chunk.content)} chars")
        
        # Test ChatMessage model
        message = ChatMessage(
            content="What are the best exercises for longevity?",
            role="user"
        )
        print(f"✅ ChatMessage model: {message.role}")
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False
    
    # Test exceptions
    print("\n🚨 Testing Exceptions...")
    try:
        try:
            raise ConfigurationError("Test configuration error")
        except ConfigurationError as e:
            print(f"✅ Exception handling: {e.error_code}")
            
    except Exception as e:
        print(f"❌ Exception test failed: {e}")
        return False
    
    print("\n🎉 All configuration tests passed!")
    return True


if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)