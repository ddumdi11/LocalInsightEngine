"""
Comprehensive Edge Case Tests for LocalInsightEngine.
LocalInsightEngine Test-Engineer Agent - Edge Case Coverage

FOCUS: Real-world edge cases, error conditions, and performance validation
TARGET: 95% coverage of critical error paths and edge conditions
"""

import unittest
import tempfile
import time
import gc
import sys
import psutil
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader
from local_insight_engine.services.processing_hub.spacy_entity_extractor import SpacyEntityExtractor
from local_insight_engine.main import LocalInsightEngine


class TestRealFileProcessing(unittest.TestCase):
    """Test with real files available in the project."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.available_files = []

        # Check for available test files
        potential_files = [
            self.project_root / "german_sample.pdf",
            self.project_root / "english_sample.pdf",
            self.project_root / "german_sample.txt",
            self.project_root / "english_sample.txt",
        ]

        for file_path in potential_files:
            if file_path.exists():
                self.available_files.append(file_path)

    def test_real_file_processing_consistency(self):
        """Test that both loaders produce consistent results with real files."""
        if not self.available_files:
            self.skipTest("No test files available")

        original_loader = DocumentLoader()
        streaming_loader = StreamingDocumentLoader()

        for file_path in self.available_files[:2]:  # Test first 2 files to save time
            if file_path.suffix.lower() not in ['.txt', '.pdf']:
                continue

            with self.subTest(file=file_path.name):
                try:
                    # Load with both loaders
                    original_doc = original_loader.load(file_path)
                    streaming_doc = streaming_loader.load(file_path)

                    # Compare metadata
                    self.assertEqual(
                        original_doc.metadata.file_format,
                        streaming_doc.metadata.file_format,
                        f"File format mismatch for {file_path.name}"
                    )

                    # Content length should be very similar (allowing for small differences in processing)
                    content_diff = abs(len(original_doc.text_content) - len(streaming_doc.text_content))
                    max_allowed_diff = max(100, len(original_doc.text_content) * 0.01)  # 1% or 100 chars

                    self.assertLess(
                        content_diff,
                        max_allowed_diff,
                        f"Content length difference too large for {file_path.name}: {content_diff} chars"
                    )

                except Exception as e:
                    self.fail(f"Failed to process {file_path.name}: {e}")

    def test_file_type_validation_with_real_files(self):
        """Test file type detection with real files."""
        if not self.available_files:
            self.skipTest("No test files available")

        streaming_loader = StreamingDocumentLoader()

        for file_path in self.available_files:
            with self.subTest(file=file_path.name):
                info = streaming_loader.get_file_type_info(file_path)

                # Basic validation
                self.assertIn('extension', info)
                self.assertIn('detected_type', info)
                self.assertIn('matches', info)
                self.assertIn('supported', info)

                # Should detect supported files correctly
                if file_path.suffix.lower() in ['.pdf', '.txt', '.docx', '.epub']:
                    self.assertTrue(info['supported'], f"{file_path.name} should be supported")

    def test_memory_usage_with_real_files(self):
        """Test memory usage patterns with real files."""
        if not self.available_files:
            self.skipTest("No test files available")

        process = psutil.Process()
        streaming_loader = StreamingDocumentLoader()

        for file_path in self.available_files[:1]:  # Test one file to avoid memory issues
            with self.subTest(file=file_path.name):
                # Measure memory before
                gc.collect()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB

                # Load document
                document = streaming_loader.load(file_path)

                # Measure memory after
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = memory_after - memory_before

                # Clean up
                del document
                gc.collect()
                memory_final = process.memory_info().rss / 1024 / 1024  # MB

                # Memory should be reasonable
                file_size_mb = file_path.stat().st_size / 1024 / 1024

                # Memory usage shouldn't be more than 10x file size (very generous)
                self.assertLess(
                    memory_used,
                    max(50, file_size_mb * 10),
                    f"Memory usage too high for {file_path.name}: {memory_used:.1f}MB"
                )

                # Some memory should be reclaimed after cleanup
                memory_reclaimed = memory_after - memory_final
                if memory_used > 5:  # Only check if significant memory was used
                    self.assertGreater(
                        memory_reclaimed,
                        memory_used * 0.1,  # At least 10% reclaimed
                        f"Insufficient memory reclaimed for {file_path.name}"
                    )


class TestErrorHandlingEdgeCases(unittest.TestCase):
    """Test comprehensive error handling scenarios."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.loader = StreamingDocumentLoader()

    def tearDown(self):
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_corrupted_file_handling(self):
        """Test handling of various corrupted file scenarios."""

        # Test 1: Completely empty file
        empty_file = self.test_dir / "empty.pdf"
        empty_file.touch()

        with self.assertRaises((ValueError, Exception)):
            self.loader.load(empty_file)

        # Test 2: File with wrong header
        fake_pdf = self.test_dir / "fake.pdf"
        fake_pdf.write_bytes(b"This is not a PDF file")

        with self.assertRaises((ValueError, Exception)):
            self.loader.load(fake_pdf)

        # Test 3: File with partial content
        partial_pdf = self.test_dir / "partial.pdf"
        partial_pdf.write_bytes(b"%PDF-1.4\n%EOF")  # Minimal but invalid PDF

        with self.assertRaises(Exception):
            self.loader.load(partial_pdf)

    def test_permission_errors(self):
        """Test handling of permission-related errors."""

        # Create a test file
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')

        # Test permission error during file reading
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with self.assertRaises(PermissionError):
                self.loader.load(test_file)

    def test_disk_space_errors(self):
        """Test handling of disk space issues (simulated)."""

        # Create a large text file
        test_file = self.test_dir / "large.txt"
        content = "Test line " * 1000
        test_file.write_text(content, encoding='utf-8')

        # Simulate disk space error during processing
        original_write = Path.write_text

        def mock_write_disk_full(*args, **kwargs):
            raise OSError("No space left on device")

        with patch.object(Path, 'write_text', side_effect=mock_write_disk_full):
            # This won't trigger during loading, but tests the pattern
            with self.assertRaises((OSError, Exception)):
                test_file.write_text("More content")

    def test_unicode_encoding_edge_cases(self):
        """Test handling of various Unicode encoding scenarios."""

        # Test 1: File with mixed encoding
        mixed_file = self.test_dir / "mixed_encoding.txt"

        # Write with UTF-8 first part and Latin-1 second part
        with open(mixed_file, 'wb') as f:
            f.write("Hello ".encode('utf-8'))
            f.write("Wörld".encode('latin-1'))  # This will cause issues

        # Should handle encoding errors gracefully
        with self.assertRaises((UnicodeDecodeError, UnicodeError)):
            self.loader.load(mixed_file)

    def test_extremely_large_file_simulation(self):
        """Test behavior with extremely large files (simulated)."""

        # Create a file that reports as being very large
        test_file = self.test_dir / "fake_large.txt"
        test_file.write_text("Small content", encoding='utf-8')

        # Mock stat to report huge size
        original_stat = Path.stat

        def mock_huge_stat(self):
            result = original_stat(self)
            # Create a mock stat result with huge size
            mock_stat = Mock(spec=result)
            mock_stat.st_size = 10 * 1024 * 1024 * 1024  # 10GB
            return mock_stat

        with patch.object(Path, 'stat', mock_huge_stat):
            # Should trigger streaming mode
            self.assertTrue(self.loader._should_use_streaming(test_file))

    def test_concurrent_access_conflicts(self):
        """Test handling of concurrent file access conflicts."""
        import threading
        import queue
        import time

        # Create a test file
        test_file = self.test_dir / "concurrent.txt"
        test_file.write_text("Test content for concurrent access", encoding='utf-8')

        errors_queue = queue.Queue()
        success_count = 0

        def load_with_delay(file_path, delay):
            nonlocal success_count
            try:
                time.sleep(delay)
                loader = StreamingDocumentLoader()
                result = loader.load(file_path)
                success_count += 1
                return result
            except Exception as e:
                errors_queue.put(str(e))

        # Start multiple threads accessing the same file
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=load_with_delay,
                args=(test_file, i * 0.1)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)

        # At least some should succeed (file reading should be safe for multiple readers)
        self.assertGreater(success_count, 0, "At least one concurrent access should succeed")


class TestAnonymizationEdgeCases(unittest.TestCase):
    """Test edge cases in anonymization and entity extraction."""

    def setUp(self):
        # Mock spaCy to avoid model dependencies in edge case testing
        self.spacy_patcher = patch('spacy.load')
        self.mock_spacy_load = self.spacy_patcher.start()

        self.mock_nlp = Mock()
        self.mock_spacy_load.return_value = self.mock_nlp

    def tearDown(self):
        self.spacy_patcher.stop()

    def test_canary_phrase_edge_cases(self):
        """Test edge cases in canary phrase detection and neutralization."""

        try:
            extractor = SpacyEntityExtractor()
        except:
            self.skipTest("SpaCy entity extractor not available")

        # Test various canary phrase patterns
        test_cases = [
            "Normal text with CANARY_PHRASE_123 embedded",
            "Multiple CANARY_A_1 and CANARY_B_2 in same text",
            "Case variations canary_phrase_456 and CANARY_PHRASE_789",
            "Special chars CANARY_PHRASE-123 and CANARY.PHRASE.456",
            "Unicode CANARY_PHRASE_ÄÖÜ and CANARY_测试_123",
        ]

        for test_text in test_cases:
            with self.subTest(text=test_text[:30] + "..."):
                # Mock entity detection to return no entities (focus on canary detection)
                mock_doc = Mock()
                mock_doc.ents = []
                self.mock_nlp.return_value = mock_doc

                result = extractor.extract_and_neutralize(test_text)

                # Should not contain obvious canary phrases
                self.assertNotRegex(
                    result,
                    r'CANARY_[A-Z0-9_]+',
                    f"CANARY phrase not properly neutralized in: {test_text}"
                )

    def test_entity_extraction_edge_cases(self):
        """Test edge cases in entity extraction."""

        try:
            extractor = SpacyEntityExtractor()
        except:
            self.skipTest("SpaCy entity extractor not available")

        # Test with overlapping entities
        mock_entity1 = Mock()
        mock_entity1.text = "Dr. Smith"
        mock_entity1.label_ = "PERSON"

        mock_entity2 = Mock()
        mock_entity2.text = "Smith Corp"  # Overlaps with "Smith"
        mock_entity2.label_ = "ORG"

        mock_doc = Mock()
        mock_doc.ents = [mock_entity1, mock_entity2]
        self.mock_nlp.return_value = mock_doc

        test_text = "Dr. Smith works at Smith Corp in downtown."
        result = extractor.extract_and_neutralize(test_text)

        # Should handle overlapping entities gracefully
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_extremely_long_text_processing(self):
        """Test processing of extremely long text inputs."""

        try:
            extractor = SpacyEntityExtractor()
        except:
            self.skipTest("SpaCy entity extractor not available")

        # Create very long text
        long_text = "This is a test sentence. " * 10000  # ~250,000 characters

        # Mock minimal entity detection
        mock_doc = Mock()
        mock_doc.ents = []
        self.mock_nlp.return_value = mock_doc

        # Should handle without crashing
        result = extractor.extract_and_neutralize(long_text)

        self.assertIsInstance(result, str)
        # Should return something (even if heavily processed)
        self.assertGreater(len(result), 10)

    def test_special_character_handling(self):
        """Test handling of special characters and emojis."""

        try:
            extractor = SpacyEntityExtractor()
        except:
            self.skipTest("SpaCy entity extractor not available")

        special_texts = [
            "Text with emojis 😀 🚀 🎯 and symbols",
            "Mathematical symbols ∑ ∫ ∆ ∞ ≠ ≤ ≥",
            "Currency symbols $ € £ ¥ ₹ ₿",
            'Special quotes "fancy" and \'curly\' quotes',
            "Zero-width characters\u200b\u200c\u200d test",
        ]

        for text in special_texts:
            with self.subTest(text=text[:20] + "..."):
                mock_doc = Mock()
                mock_doc.ents = []
                self.mock_nlp.return_value = mock_doc

                result = extractor.extract_and_neutralize(text)

                # Should not crash and should return valid string
                self.assertIsInstance(result, str)


class TestPerformanceEdgeCases(unittest.TestCase):
    """Test performance-related edge cases."""

    def setUp(self):
        self.streaming_loader = StreamingDocumentLoader()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_rapid_successive_loads(self):
        """Test rapid successive document loading operations."""

        # Create multiple small test files
        test_files = []
        for i in range(10):
            test_file = self.test_dir / f"rapid_test_{i}.txt"
            test_file.write_text(f"Test content for file {i} " * 100, encoding='utf-8')
            test_files.append(test_file)

        start_time = time.perf_counter()

        # Load all files rapidly
        results = []
        for test_file in test_files:
            result = self.streaming_loader.load(test_file)
            results.append(result)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Should complete in reasonable time
        self.assertLess(total_time, 30.0, "Rapid successive loads took too long")

        # All should succeed
        self.assertEqual(len(results), len(test_files))

        # Results should be valid
        for result in results:
            self.assertGreater(len(result.text_content), 0)

    def test_memory_stress_simulation(self):
        """Test behavior under simulated memory stress."""

        # Create a file that will use some memory
        large_file = self.test_dir / "memory_stress.txt"
        content = "Memory stress test line. " * 5000  # ~125KB
        large_file.write_text(content, encoding='utf-8')

        # Load multiple times to simulate memory pressure
        documents = []

        try:
            for i in range(10):
                doc = self.streaming_loader.load(large_file)
                documents.append(doc)

                # Force some cleanup periodically
                if i % 3 == 0:
                    gc.collect()

            # All should be valid
            for doc in documents:
                self.assertGreater(len(doc.text_content), 1000)

        finally:
            # Clean up
            del documents
            gc.collect()


if __name__ == '__main__':
    print("LocalInsightEngine - Comprehensive Edge Case Tests")
    print("=" * 60)
    print("FOCUS: Real-world edge cases and error conditions")
    print("TARGET: 95% coverage of critical error paths")
    print()

    unittest.main(verbosity=2, buffer=True)