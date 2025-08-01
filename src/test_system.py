"""
Test suite for the Agentic RAG system
Contains unit tests and integration tests for all major components
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
try:
    from config import ConfigManager, AzureOpenAIConfig, AzureSearchConfig, ApplicationConfig
    from utils import (
        clean_text, truncate_text, extract_keywords, generate_content_hash,
        format_timestamp, safe_json_parse, batch_list, validate_url,
        sanitize_filename, calculate_text_similarity, PerformanceTracker
    )
    from prompts import PLANNING_PROMPT, ANSWER_PROMPT
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    IMPORTS_AVAILABLE = False

class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
    
    def test_azure_openai_config_validation(self):
        """Test Azure OpenAI configuration validation"""
        # Valid configuration
        valid_config = AzureOpenAIConfig(
            endpoint="https://test.openai.azure.com/",
            api_key="test-key",
            api_version="2024-02-15-preview",
            chat_deployment="gpt-4",
            embeddings_deployment="text-embedding-ada-002"
        )
        self.assertTrue(valid_config.validate())
        
        # Invalid configuration (missing endpoint)
        invalid_config = AzureOpenAIConfig(
            endpoint="",
            api_key="test-key",
            api_version="2024-02-15-preview",
            chat_deployment="gpt-4",
            embeddings_deployment="text-embedding-ada-002"
        )
        self.assertFalse(invalid_config.validate())
    
    def test_azure_search_config_validation(self):
        """Test Azure Search configuration validation"""
        # Valid configuration
        valid_config = AzureSearchConfig(
            endpoint="https://test.search.windows.net",
            api_key="test-key",
            index_name="test-index",
            api_version="2023-11-01"
        )
        self.assertTrue(valid_config.validate())
        
        # Invalid configuration (missing index name)
        invalid_config = AzureSearchConfig(
            endpoint="https://test.search.windows.net",
            api_key="test-key",
            index_name="",
            api_version="2023-11-01"
        )
        self.assertFalse(invalid_config.validate())
    
    def test_application_config_validation(self):
        """Test application configuration validation"""
        # Valid configuration
        valid_config = ApplicationConfig(
            log_level="INFO",
            max_search_results=20,
            max_concurrent_searches=5,
            enable_conversation_memory=True,
            conversation_memory_window=5
        )
        self.assertTrue(valid_config.validate())
        
        # Invalid configuration (negative values)
        invalid_config = ApplicationConfig(
            log_level="INFO",
            max_search_results=-1,
            max_concurrent_searches=5,
            enable_conversation_memory=True,
            conversation_memory_window=5
        )
        self.assertFalse(invalid_config.validate())

class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
    
    def test_clean_text(self):
        """Test text cleaning function"""
        # Test basic cleaning
        dirty_text = "  This   is   a   test!  @#$%  "
        cleaned = clean_text(dirty_text)
        self.assertNotIn("  ", cleaned)  # No double spaces
        self.assertNotIn("@#$%", cleaned)  # Special chars removed
        
        # Test empty input
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")
    
    def test_truncate_text(self):
        """Test text truncation function"""
        long_text = "This is a very long text that should be truncated"
        
        # Test normal truncation
        truncated = truncate_text(long_text, 20)
        self.assertTrue(len(truncated) <= 20)
        self.assertTrue(truncated.endswith("..."))
        
        # Test no truncation needed
        short_text = "Short"
        self.assertEqual(truncate_text(short_text, 20), short_text)
    
    def test_extract_keywords(self):
        """Test keyword extraction function"""
        text = "This is a test document about automotive standards and regulations"
        keywords = extract_keywords(text, max_keywords=5)
        
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) <= 5)
        self.assertIn("automotive", keywords)
        self.assertIn("standards", keywords)
        self.assertNotIn("this", keywords)  # Stop word should be removed
    
    def test_generate_content_hash(self):
        """Test content hash generation"""
        text1 = "This is a test"
        text2 = "This is a test"
        text3 = "This is different"
        
        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)
        hash3 = generate_content_hash(text3)
        
        # Same content should have same hash
        self.assertEqual(hash1, hash2)
        
        # Different content should have different hash
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be non-empty
        self.assertTrue(len(hash1) > 0)
    
    def test_safe_json_parse(self):
        """Test safe JSON parsing"""
        # Valid JSON
        valid_json = '{"key": "value"}'
        result = safe_json_parse(valid_json)
        self.assertEqual(result["key"], "value")
        
        # Invalid JSON
        invalid_json = '{"key": invalid}'
        result = safe_json_parse(invalid_json, default={})
        self.assertEqual(result, {})
    
    def test_batch_list(self):
        """Test list batching function"""
        items = list(range(10))
        batches = batch_list(items, 3)
        
        self.assertEqual(len(batches), 4)  # 10 items, batch size 3 = 4 batches
        self.assertEqual(batches[0], [0, 1, 2])
        self.assertEqual(batches[-1], [9])  # Last batch has 1 item
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://localhost:8080"))
        self.assertTrue(validate_url("https://api.openai.azure.com/"))
        
        # Invalid URLs
        self.assertFalse(validate_url("not-a-url"))
        self.assertFalse(validate_url(""))
        self.assertFalse(validate_url("ftp://example.com"))
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test with invalid characters
        dirty_name = 'file<>:"/\\|?*.txt'
        clean_name = sanitize_filename(dirty_name)
        
        # Should not contain invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            self.assertNotIn(char, clean_name)
        
        # Should not be empty
        self.assertTrue(len(clean_name) > 0)
    
    def test_calculate_text_similarity(self):
        """Test text similarity calculation"""
        text1 = "automotive safety standards"
        text2 = "safety standards for automotive"
        text3 = "completely different topic"
        
        # Similar texts should have high similarity
        similarity_high = calculate_text_similarity(text1, text2)
        self.assertGreater(similarity_high, 0.5)
        
        # Different texts should have low similarity
        similarity_low = calculate_text_similarity(text1, text3)
        self.assertLess(similarity_low, 0.5)
        
        # Empty texts should have zero similarity
        self.assertEqual(calculate_text_similarity("", "test"), 0.0)
    
    def test_performance_tracker(self):
        """Test performance tracking utility"""
        tracker = PerformanceTracker()
        
        # Start and end timer
        tracker.start_timer("test_operation")
        import time
        time.sleep(0.01)  # Small delay
        duration = tracker.end_timer("test_operation")
        
        # Duration should be positive
        self.assertGreater(duration, 0)
        
        # Metrics should be available
        metrics = tracker.get_metrics()
        self.assertIn("test_operation", metrics)
        self.assertIn("duration", metrics["test_operation"])

class TestPrompts(unittest.TestCase):
    """Test prompt templates"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
    
    def test_prompt_formatting(self):
        """Test that prompts can be formatted with parameters"""
        # Test planning prompt
        formatted_planning = PLANNING_PROMPT.format(
            question="What are automotive standards?",
            conversation_history="Previous discussion about cars"
        )
        
        self.assertIn("What are automotive standards?", formatted_planning)
        self.assertIn("Previous discussion about cars", formatted_planning)
        
        # Test answer prompt
        formatted_answer = ANSWER_PROMPT.format(
            question="What are safety standards?",
            context="Safety standards include...",
            conversation_history="Previous context"
        )
        
        self.assertIn("What are safety standards?", formatted_answer)
        self.assertIn("Safety standards include...", formatted_answer)
    
    def test_prompt_content(self):
        """Test that prompts contain expected content"""
        # Planning prompt should mention search queries
        self.assertIn("search", PLANNING_PROMPT.lower())
        self.assertIn("query", PLANNING_PROMPT.lower())
        
        # Answer prompt should mention context usage
        self.assertIn("context", ANSWER_PROMPT.lower())
        self.assertIn("information", ANSWER_PROMPT.lower())

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        # Create temporary environment file
        self.temp_env = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        self.temp_env.write("""
AZURE_OPENAI_ENDPOINT=https://test.openai.azure.com/
AZURE_OPENAI_KEY=test-key
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_SEARCH_ENDPOINT=https://test.search.windows.net
AZURE_SEARCH_KEY=test-key
AZURE_SEARCH_INDEX_NAME=test-index
        """)
        self.temp_env.close()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_env'):
            os.unlink(self.temp_env.name)
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_KEY': 'test-key',
        'AZURE_OPENAI_CHAT_DEPLOYMENT': 'gpt-4',
        'AZURE_SEARCH_ENDPOINT': 'https://test.search.windows.net',
        'AZURE_SEARCH_KEY': 'test-key',
        'AZURE_SEARCH_INDEX_NAME': 'test-index'
    })
    def test_config_manager_initialization(self):
        """Test that ConfigManager initializes with valid environment"""
        try:
            config = ConfigManager(env_file=self.temp_env.name)
            
            # Should not raise an exception
            self.assertIsNotNone(config.azure_openai)
            self.assertIsNotNone(config.azure_search)
            self.assertIsNotNone(config.application)
            
            # Test getting configurations
            openai_config = config.get_azure_openai_config()
            search_config = config.get_azure_search_config()
            
            self.assertIn("azure_endpoint", openai_config)
            self.assertIn("endpoint", search_config)
            
        except Exception as e:
            self.fail(f"ConfigManager initialization failed: {e}")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfig,
        TestUtils,
        TestPrompts,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running Agentic RAG System Tests...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
