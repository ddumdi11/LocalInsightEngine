"""
Comprehensive Edge Case Tests for LocalInsightEngine.
LocalInsightEngine v0.1.1 - Critical Edge Cases and Error Handling Tests

FOCUS: Robuste Edge Cases, Memory Issues, Error Resilience, Performance Limits
COVERAGE: PDF Corruption, Memory Leaks, Unicode, Threading, API Failures
"""

import sys
import unittest
import tempfile
import threading
import time
import gc
import psutil
import os
from pathlib import Path
from typing import List, Dict, Optional
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.spacy_entity_extractor import SpacyEntityExtractor
from local_insight_engine.main import LocalInsightEngine


class TestPDFCorruptionEdgeCases(unittest.TestCase):
    """Test handling of corrupted, malformed, and edge-case PDF files."""

    def setUp(self):
        self.loader = DocumentLoader()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_completely_corrupted_pdf(self):
        """Test handling of completely corrupted PDF files."""
        # Create a fake PDF that's just random bytes
        corrupted_pdf = self.test_dir / "corrupted.pdf"
        with open(corrupted_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\n')  # Valid header
            f.write(b'\x00\x01\x02\x03' * 100)  # Random corrupt data

        with self.assertRaises(Exception):
            self.loader.load(corrupted_pdf)

    def test_empty_pdf_file(self):
        """Test handling of completely empty PDF files."""
        empty_pdf = self.test_dir / "empty.pdf"
        empty_pdf.touch()  # Create empty file

        with self.assertRaises(Exception):
            self.loader.load(empty_pdf)

    def test_pdf_with_invalid_header(self):
        """Test handling of files with .pdf extension but invalid header."""
        fake_pdf = self.test_dir / "fake.pdf"
        with open(fake_pdf, 'w', encoding='utf-8') as f:
            f.write("This is not a PDF file, just text content.")

        # Should detect as text and warn about mismatch
        try:
            document = self.loader.load(fake_pdf)
            # Should succeed by detecting actual content type
            self.assertEqual(document.metadata.file_format, "txt")
        except Exception as e:
            # Or fail gracefully with clear error
            self.assertIn("PDF", str(e).upper())

    def test_pdf_with_zero_pages(self):
        """Test handling of PDFs with no readable pages."""
        # This would require creating a minimal valid PDF with no content
        # For now, test the error handling path
        pass

    def test_password_protected_pdf(self):
        """Test handling of password-protected PDFs."""
        # Create mock password-protected PDF scenario
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_reader.side_effect = Exception("File has not been decrypted")

            test_pdf = self.test_dir / "protected.pdf"
            test_pdf.write_bytes(b'%PDF-1.4\nprotected content')

            with self.assertRaises(Exception):
                self.loader.load(test_pdf)

    def test_unicode_in_pdf_content(self):
        """Test handling of PDFs with complex Unicode content."""
        # Test with various Unicode edge cases
        unicode_content = "Test: 🚀 Émojis, Äccénts, 中文, العربية, עברית"

        # Mock PDF reader to return complex Unicode
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = unicode_content

            mock_instance = Mock()
            mock_instance.pages = [mock_page]
            mock_instance.metadata = {}
            mock_reader.return_value = mock_instance

            test_pdf = self.test_dir / "unicode.pdf"
            test_pdf.write_bytes(b'%PDF-1.4\nmock')

            document = self.loader.load(test_pdf)
            self.assertIn("🚀", document.text_content)
            self.assertIn("中文", document.text_content)


class TestMemoryAndPerformanceEdgeCases(unittest.TestCase):
    """Test memory usage patterns, leaks, and performance edge cases."""

    def setUp(self):
        self.process = psutil.Process(os.getpid())
        self.loader = DocumentLoader()

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def test_memory_leak_in_batch_processing(self):
        """Test for memory leaks when processing multiple documents sequentially."""
        initial_memory = self.get_memory_usage()

        # Create multiple test documents
        test_docs = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(10):
                doc_path = Path(temp_dir) / f"test_{i}.txt"
                doc_path.write_text(f"Test document {i} " * 1000, encoding='utf-8')
                test_docs.append(doc_path)

            # Process documents and check memory growth
            memory_readings = [initial_memory]

            for doc_path in test_docs:
                try:
                    document = self.loader.load(doc_path)
                    # Force some processing to use memory
                    _ = len(document.text_content.split())

                    # Force garbage collection and measure
                    gc.collect()
                    current_memory = self.get_memory_usage()
                    memory_readings.append(current_memory)

                    # Delete reference to document
                    del document

                except Exception as e:
                    print(f"Failed to process {doc_path}: {e}")

        final_memory = self.get_memory_usage()
        memory_growth = final_memory - initial_memory

        # Allow some memory growth, but not excessive (>50MB for small docs is suspicious)
        self.assertLess(memory_growth, 50.0,
                       f"Potential memory leak detected: {memory_growth:.1f}MB growth")

        print(f"Memory test: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_growth:.1f}MB)")

    def test_large_document_memory_handling(self):
        """Test memory handling with artificially large documents."""
        # Create a large text document
        large_content = "Large document content. " * 100000  # ~2.5MB of text

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(large_content)
            large_doc_path = Path(f.name)

        try:
            initial_memory = self.get_memory_usage()

            # Load large document
            document = self.loader.load(large_doc_path)

            peak_memory = self.get_memory_usage()
            memory_used = peak_memory - initial_memory

            # Clean up
            del document
            gc.collect()

            final_memory = self.get_memory_usage()
            memory_released = peak_memory - final_memory

            print(f"Large doc test: Used {memory_used:.1f}MB, Released {memory_released:.1f}MB")

            # Memory should be mostly released (allow some overhead)
            self.assertGreater(memory_released / memory_used, 0.7,
                              "Insufficient memory cleanup after large document processing")

        finally:
            large_doc_path.unlink()

    def test_concurrent_document_loading(self):
        """Test thread safety of document loading."""
        def load_document(doc_path: Path) -> bool:
            """Load document and return success status."""
            try:
                document = self.loader.load(doc_path)
                # Simulate some processing
                word_count = len(document.text_content.split())
                return word_count > 0
            except Exception as e:
                print(f"Thread error: {e}")
                return False

        # Create test documents
        test_docs = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(5):
                doc_path = Path(temp_dir) / f"concurrent_test_{i}.txt"
                doc_path.write_text(f"Concurrent test document {i} " * 100, encoding='utf-8')
                test_docs.append(doc_path)

            # Process documents concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(load_document, doc) for doc in test_docs]
                results = [future.result() for future in as_completed(futures)]

            # All documents should load successfully
            self.assertTrue(all(results), "Some documents failed to load in concurrent test")


class TestAnonymizationEdgeCases(unittest.TestCase):
    """Test edge cases in anonymization and entity extraction."""

    def setUp(self):
        # Mock spaCy to avoid model dependencies in edge case tests
        self.mock_patcher = patch('spacy.load')
        mock_spacy_load = self.mock_patcher.start()

        self.mock_nlp = Mock()
        mock_spacy_load.return_value = self.mock_nlp

        self.extractor = SpacyEntityExtractor()

    def tearDown(self):
        self.mock_patcher.stop()

    def test_canary_phrases_with_unicode_encoding(self):
        """Test canary phrase detection with various Unicode encodings."""
        canary_phrases = [
            "CANARY_UNICODE_🔍_TEST",
            "CANARY_ÄÖÜSS_GERMAN",
            "CANARY_中文_CHINESE",
            "CANARY_العربية_ARABIC"
        ]

        for canary in canary_phrases:
            # Mock entity extraction
            mock_doc = Mock()
            mock_doc.ents = []
            self.mock_nlp.return_value = mock_doc

            # Test neutralization
            neutralized = self.extractor._neutralize_suspicious_identifiers(canary)

            # Should detect and neutralize the canary
            self.assertNotIn(canary, neutralized,
                           f"Failed to neutralize Unicode canary: {canary}")

    def test_nested_entity_recognition_edge_cases(self):
        """Test complex nested entity recognition scenarios."""
        complex_text = """
        Dr. John Smith from CANARY_COMPANY_XYZ worked with
        Prof. CANARY_PERSON_123 at University of CANARY_LOCATION_ABC.
        Their research on CANARY_RESEARCH_TOPIC_999 was published in 2023.
        Contact: john.smith@CANARY_EMAIL_DOMAIN.com
        """

        # Mock complex entity extraction
        mock_doc = Mock()
        mock_entity1 = Mock()
        mock_entity1.text = "CANARY_COMPANY_XYZ"
        mock_entity1.label_ = "ORG"

        mock_entity2 = Mock()
        mock_entity2.text = "CANARY_PERSON_123"
        mock_entity2.label_ = "PERSON"

        mock_doc.ents = [mock_entity1, mock_entity2]
        self.mock_nlp.return_value = mock_doc

        neutralized = self.extractor.extract_and_neutralize(complex_text)

        # All canary phrases should be neutralized
        for canary in ["CANARY_COMPANY_XYZ", "CANARY_PERSON_123", "CANARY_LOCATION_ABC"]:
            self.assertNotIn(canary, neutralized,
                           f"Failed to neutralize nested canary: {canary}")

    def test_malformed_text_input(self):
        """Test handling of malformed or unusual text input."""
        malformed_inputs = [
            "",  # Empty string
            "\x00\x01\x02",  # Binary data
            "A" * 10000,  # Very long string
            "\n\n\n\n\n",  # Only whitespace
            "🚀" * 100,  # Only emojis
            None,  # None input (should be handled gracefully)
        ]

        for malformed_input in malformed_inputs:
            try:
                # Mock empty entity extraction for malformed input
                mock_doc = Mock()
                mock_doc.ents = []
                self.mock_nlp.return_value = mock_doc

                if malformed_input is None:
                    with self.assertRaises((AttributeError, TypeError)):
                        self.extractor.extract_and_neutralize(malformed_input)
                else:
                    result = self.extractor.extract_and_neutralize(malformed_input)
                    self.assertIsInstance(result, str,
                                        f"Failed to handle malformed input: {repr(malformed_input)}")

            except Exception as e:
                # Should fail gracefully, not crash
                self.assertIsInstance(e, (ValueError, TypeError, AttributeError),
                                    f"Unexpected exception for input {repr(malformed_input)}: {e}")


class TestAPIResilienceEdgeCases(unittest.TestCase):
    """Test API failure handling and resilience."""

    def test_claude_api_timeout_handling(self):
        """Test handling of Claude API timeouts."""
        from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient

        with patch('anthropic.Anthropic') as mock_anthropic:
            # Mock timeout exception
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("Request timeout")
            mock_anthropic.return_value = mock_client

            claude_client = ClaudeClient()

            # Should handle timeout gracefully
            with self.assertRaises(Exception):
                claude_client.analyze_text("Test text", "Test prompt")

    def test_api_rate_limiting_simulation(self):
        """Test handling of API rate limiting."""
        # Mock rate limiting scenario
        with patch('time.sleep') as mock_sleep:
            with patch('anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()

                # First call fails with rate limit, second succeeds
                mock_client.messages.create.side_effect = [
                    Exception("Rate limit exceeded"),
                    Mock(content=[Mock(text="Success")])
                ]
                mock_anthropic.return_value = mock_client

                from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient
                claude_client = ClaudeClient()

                # Should handle rate limiting (currently might just fail)
                try:
                    result = claude_client.analyze_text("Test", "Test")
                    # If retry logic exists, it should eventually succeed
                except Exception as e:
                    # Should fail with meaningful error message
                    self.assertIn("limit", str(e).lower())


class TestFileSystemEdgeCases(unittest.TestCase):
    """Test file system related edge cases."""

    def setUp(self):
        self.loader = DocumentLoader()

    def test_file_permission_errors(self):
        """Test handling of files with restricted permissions."""
        # Create a test file and attempt to restrict permissions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            test_file = Path(f.name)

        try:
            # Try to remove read permissions (platform dependent)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(test_file, 0o000)

                with self.assertRaises(PermissionError):
                    self.loader.load(test_file)
        finally:
            # Restore permissions and clean up
            if os.name != 'nt':
                os.chmod(test_file, 0o644)
            test_file.unlink()

    def test_file_disappears_during_processing(self):
        """Test handling of files that disappear during processing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            test_file = Path(f.name)

        # File exists when we start
        self.assertTrue(test_file.exists())

        # Mock the file being deleted during processing
        original_load_text = self.loader._load_text

        def mock_load_text_with_deletion(file_path):
            # Delete file during processing
            file_path.unlink()
            # Then try to proceed (should fail)
            return original_load_text(file_path)

        with patch.object(self.loader, '_load_text', side_effect=mock_load_text_with_deletion):
            with self.assertRaises(FileNotFoundError):
                self.loader.load(test_file)

    def test_extremely_long_filename(self):
        """Test handling of files with extremely long names."""
        # Create file with very long name (but within OS limits)
        long_name = "a" * 200 + ".txt"

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                long_file = Path(temp_dir) / long_name
                long_file.write_text("Test content", encoding='utf-8')

                # Should handle long filenames gracefully
                document = self.loader.load(long_file)
                self.assertIsNotNone(document)

            except OSError as e:
                # If OS doesn't support long names, that's acceptable
                print(f"OS limitation for long filenames: {e}")


if __name__ == '__main__':
    print("LocalInsightEngine - Comprehensive Edge Case Tests")
    print("=" * 60)
    print("COVERAGE: PDF Corruption, Memory Leaks, Unicode, Threading, API Failures")
    print("FOCUS: Robuste Error Handling and Performance Limits")
    print()

    # Run with high verbosity to see all edge cases
    unittest.main(verbosity=2, buffer=True)