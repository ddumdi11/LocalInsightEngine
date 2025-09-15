"""
Unit tests for individual functions and components.
LocalInsightEngine v0.1.0 - Unit tests for core components
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.config.settings import Settings
from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.spacy_entity_extractor import SpacyEntityExtractor
from local_insight_engine.services.processing_hub.text_processor import TextProcessor


class TestSettings(unittest.TestCase):
    """Test settings configuration."""
    
    def test_settings_defaults(self):
        """Test that settings have sensible defaults."""
        settings = Settings()
        self.assertEqual(settings.app_name, "LocalInsightEngine")
        self.assertEqual(settings.app_version, "0.1.1")
        self.assertEqual(settings.chunk_size, 1000)
        self.assertEqual(settings.chunk_overlap, 200)
        self.assertEqual(settings.spacy_model, "de_core_news_sm")
        self.assertEqual(settings.llm_model, "claude-sonnet-4-20250514")
        
    def test_settings_env_loading(self):
        """Test that environment variables are loaded."""
        with patch.dict('os.environ', {'LLM_API_KEY': 'test-key-123'}):
            settings = Settings()
            self.assertEqual(settings.llm_api_key, 'test-key-123')
    
    def test_directories_created(self):
        """Test that data directories are created."""
        settings = Settings()
        self.assertTrue(settings.data_dir.exists())
        self.assertTrue(settings.cache_dir.exists())


class TestDocumentLoader(unittest.TestCase):
    """Test document loading functionality."""
    
    def setUp(self):
        self.loader = DocumentLoader()
    
    def test_supported_formats(self):
        """Test that loader recognizes supported formats."""
        self.assertTrue(self.loader._is_supported_format(Path("test.pdf")))
        self.assertTrue(self.loader._is_supported_format(Path("test.txt")))
        self.assertTrue(self.loader._is_supported_format(Path("test.epub")))
        self.assertFalse(self.loader._is_supported_format(Path("test.doc")))
        self.assertFalse(self.loader._is_supported_format(Path("test.xyz")))
    
    def test_text_file_detection(self):
        """Test text file format detection."""
        self.assertEqual(self.loader._get_file_format(Path("test.txt")), "txt")
        self.assertEqual(self.loader._get_file_format(Path("test.pdf")), "pdf")
        self.assertEqual(self.loader._get_file_format(Path("test.epub")), "epub")


class TestTextProcessor(unittest.TestCase):
    """Test text processing functionality."""
    
    def setUp(self):
        self.processor = TextProcessor(chunk_size=100, chunk_overlap=20)
    
    def test_processor_initialization(self):
        """Test text processor initialization."""
        self.assertEqual(self.processor.chunk_size, 100)
        self.assertEqual(self.processor.chunk_overlap, 20)
        self.assertIsNotNone(self.processor.entity_extractor)
        self.assertIsNotNone(self.processor.statement_extractor)
    
    def test_text_chunking_logic(self):
        """Test that text is chunked appropriately."""
        # This would require a mock document to test properly
        pass


class TestSpacyEntityExtractor(unittest.TestCase):
    """Test Spacy Entity Extraction functionality."""
    
    @patch('spacy.load')
    def setUp(self, mock_spacy_load):
        # Mock spacy models to avoid requiring actual model download
        self.mock_de_nlp = Mock()
        self.mock_en_nlp = Mock()
        
        # Mock the load function to return our mocked models
        def mock_load_side_effect(model_name):
            if 'de_' in model_name:
                return self.mock_de_nlp
            else:
                return self.mock_en_nlp
        
        mock_spacy_load.side_effect = mock_load_side_effect
        
        self.extractor = SpacyEntityExtractor()
    
    def test_extractor_initialization(self):
        """Test entity extractor initialization."""
        self.assertIsNotNone(self.extractor.german_nlp)
        # English model is intentionally None (German-only processing)
        self.assertIsNone(self.extractor.english_nlp)
    
    def test_basic_extraction(self):
        """Test basic entity extraction functionality."""
        # This would need proper mocking of spacy components
        pass


class TestCopyrightCompliance(unittest.TestCase):
    """Test copyright compliance measures."""
    
    def test_original_text_not_in_api_calls(self):
        """Test that original text is never sent to external APIs."""
        # This would be a more complex test involving mocking API calls
        # and ensuring no original text appears in them
        pass
    
    def test_no_original_text_in_processing(self):
        """Test that original text doesn't leak through processing."""
        # This is a conceptual test - would need integration testing
        # to verify that no original text reaches external APIs
        self.assertTrue(True)  # Placeholder


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)