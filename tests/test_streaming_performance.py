"""
Focused performance tests for StreamingDocumentLoader.
LocalInsightEngine - Performance Test Suite for Test-Engineer Agent

FOCUS: Edge cases, memory efficiency, and performance validation
TARGET: 95% coverage of critical performance paths
"""

import unittest
import tempfile
import time
import os
import gc
import sys
import logging
from pathlib import Path
from typing import Dict, Any
import psutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader

logger = logging.getLogger(__name__)


class TestStreamingDocumentLoaderPerformance(unittest.TestCase):
    """Test performance optimizations in StreamingDocumentLoader."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_loader = DocumentLoader()
        self.streaming_loader = StreamingDocumentLoader()
        self.test_dir = Path(tempfile.mkdtemp())
        self.process = psutil.Process(os.getpid())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def _create_test_pdf(self, content: str, filename: str) -> Path:
        """Create a test PDF file with given content."""
        # For testing, create a mock PDF-like file
        pdf_file = self.test_dir / filename
        pdf_content = b'%PDF-1.4\n' + content.encode('utf-8')
        pdf_file.write_bytes(pdf_content)
        return pdf_file

    def _create_large_text_file(self, size_kb: int = 100) -> Path:
        """Create a large text file for streaming tests."""
        content_lines = []
        line = "This is a test line for performance testing. " * 10  # ~470 chars per line

        # Calculate lines needed to reach desired size
        target_size = size_kb * 1024
        lines_needed = target_size // len(line)

        for i in range(lines_needed):
            content_lines.append(f"Line {i+1}: {line}")

        content = "\n\n".join(content_lines)

        text_file = self.test_dir / f"large_test_{size_kb}kb.txt"
        text_file.write_text(content, encoding='utf-8')

        return text_file

    def _measure_memory_usage(self, func, *args):
        """Measure memory usage of a function call."""
        gc.collect()
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB

        start_time = time.perf_counter()
        result = func(*args)
        end_time = time.perf_counter()

        memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        gc.collect()  # Clean up

        return {
            'result': result,
            'time_seconds': end_time - start_time,
            'memory_mb': memory_used,
            'success': True
        }

    def test_file_type_detection_performance(self):
        """Test that optimized file type detection is faster."""
        # Create various test files
        test_files = []

        # PDF
        pdf_file = self._create_test_pdf("Test PDF content", "test.pdf")
        test_files.append(pdf_file)

        # Text
        text_file = self.test_dir / "test.txt"
        text_file.write_text("Test text content", encoding='utf-8')
        test_files.append(text_file)

        # DOCX (fake)
        docx_file = self.test_dir / "test.docx"
        docx_file.write_bytes(b'PK\x03\x04' + b'word' * 100)  # ZIP signature + word content
        test_files.append(docx_file)

        total_time_original = 0
        total_time_streaming = 0

        for file_path in test_files:
            # Test original loader detection time
            start = time.perf_counter()
            try:
                original_info = self.original_loader.get_file_type_info(file_path)
            except:
                original_info = {'detected_type': 'unknown'}
            end = time.perf_counter()
            total_time_original += (end - start)

            # Test streaming loader detection time
            start = time.perf_counter()
            streaming_info = self.streaming_loader.get_file_type_info(file_path)
            end = time.perf_counter()
            total_time_streaming += (end - start)

            # Validate results are consistent
            self.assertEqual(
                original_info.get('detected_type'),
                streaming_info.get('detected_type'),
                f"File type detection mismatch for {file_path.name}"
            )

        # Streaming should be at least as fast (or faster due to optimizations)
        self.assertLessEqual(
            total_time_streaming,
            total_time_original * 1.2,  # Allow 20% tolerance
            "Streaming loader file detection should not be significantly slower"
        )

    def test_memory_efficiency_with_streaming_threshold(self):
        """Test that streaming mode is activated for large files."""
        # Create files of different sizes
        small_file = self._create_large_text_file(10)  # 10KB - should not stream
        large_file = self._create_large_text_file(200)  # 200KB - should stream

        # Test small file (no streaming)
        loader_small = StreamingDocumentLoader(memory_threshold_mb=0.1)  # 100KB threshold
        should_stream_small = loader_small._should_use_streaming(small_file)
        self.assertFalse(should_stream_small, "Small file should not trigger streaming")

        # Test large file (streaming)
        should_stream_large = loader_small._should_use_streaming(large_file)
        self.assertTrue(should_stream_large, "Large file should trigger streaming")

        # Test streaming disabled
        loader_no_stream = StreamingDocumentLoader(enable_streaming=False)
        should_not_stream = loader_no_stream._should_use_streaming(large_file)
        self.assertFalse(should_not_stream, "Streaming should be disabled when configured")

    def test_text_loading_performance_comparison(self):
        """Compare text loading performance between loaders."""
        # Create a moderately sized text file
        text_file = self._create_large_text_file(50)  # 50KB

        # Test original loader
        original_metrics = self._measure_memory_usage(
            self.original_loader.load, text_file
        )

        # Test streaming loader
        streaming_metrics = self._measure_memory_usage(
            self.streaming_loader.load, text_file
        )

        # Both should succeed
        self.assertTrue(original_metrics['success'])
        self.assertTrue(streaming_metrics['success'])

        # Results should be equivalent
        original_doc = original_metrics['result']
        streaming_doc = streaming_metrics['result']

        self.assertEqual(
            original_doc.metadata.word_count,
            streaming_doc.metadata.word_count,
            "Word count should match between loaders"
        )

        self.assertEqual(
            len(original_doc.text_content),
            len(streaming_doc.text_content),
            "Content length should match"
        )

        # Performance comparison
        logger.info(f"\nText Loading Performance Comparison:")
        logger.info(f"Original:  {original_metrics['time_seconds']:.3f}s, {original_metrics['memory_mb']:.1f}MB")
        logger.info(f"Streaming: {streaming_metrics['time_seconds']:.3f}s, {streaming_metrics['memory_mb']:.1f}MB")

        # Streaming should not be significantly slower
        self.assertLess(
            streaming_metrics['time_seconds'],
            original_metrics['time_seconds'] * 2.0,
            "Streaming loader should not be more than 2x slower"
        )

    def test_error_handling_in_streaming_mode(self):
        """Test error handling specific to streaming operations."""
        # Test with corrupted file that triggers streaming
        large_corrupt_file = self.test_dir / "corrupt_large.txt"
        large_corrupt_file.write_bytes(b'\x00' * (200 * 1024))  # 200KB of null bytes

        # Should handle gracefully
        with self.assertRaises(UnicodeDecodeError):
            self.streaming_loader.load(large_corrupt_file)

        # Test with file that disappears during processing
        disappearing_file = self._create_large_text_file(100)

        # Mock the streaming process to simulate file deletion mid-process
        original_open = open

        def mock_open(*args, **kwargs):
            # Delete file on first read attempt
            if disappearing_file.exists():
                disappearing_file.unlink()
            return original_open(*args, **kwargs)

        # This should raise a FileNotFoundError
        with unittest.mock.patch('builtins.open', side_effect=mock_open):
            with self.assertRaises(FileNotFoundError):
                self.streaming_loader.load(disappearing_file)

    def test_memory_cleanup_during_streaming(self):
        """Test that memory is properly cleaned up during streaming operations."""
        # Create a large file that will trigger streaming
        large_file = self._create_large_text_file(300)  # 300KB

        # Monitor memory before, during, and after
        initial_memory = self.process.memory_info().rss / 1024 / 1024

        # Load with streaming
        result = self.streaming_loader.load(large_file)

        # Memory after loading
        post_load_memory = self.process.memory_info().rss / 1024 / 1024

        # Clean up and measure final memory
        del result
        gc.collect()
        final_memory = self.process.memory_info().rss / 1024 / 1024

        memory_increase = post_load_memory - initial_memory
        memory_after_cleanup = final_memory - initial_memory

        logger.info(f"\nMemory Usage During Streaming:")
        logger.info(f"Initial: {initial_memory:.1f}MB")
        logger.info(f"Post-load: {post_load_memory:.1f}MB (+{memory_increase:.1f}MB)")
        logger.info(f"After cleanup: {final_memory:.1f}MB (+{memory_after_cleanup:.1f}MB)")

        # Memory should be reclaimed after cleanup
        self.assertLess(
            memory_after_cleanup,
            memory_increase * 0.8,  # At least 20% should be reclaimed
            "Memory should be properly reclaimed after document processing"
        )

    def test_processing_stats_accuracy(self):
        """Test that processing statistics are accurate."""
        # Create test files
        text_file = self._create_large_text_file(50)

        # Load and check stats
        document = self.streaming_loader.load(text_file)
        stats = self.streaming_loader.get_processing_stats()

        # Validate stats make sense
        self.assertGreater(stats.total_chars, 0, "Should have processed characters")
        self.assertEqual(stats.total_chars, len(document.text_content), "Character count should match")
        self.assertGreater(stats.paragraphs_processed, 0, "Should have processed paragraphs")
        self.assertEqual(stats.paragraphs_processed, len(document.paragraph_mapping), "Paragraph count should match")

    def test_concurrent_loading_safety(self):
        """Test that concurrent loading operations don't interfere."""
        import threading
        import queue

        # Create multiple test files
        files = [
            self._create_large_text_file(30),
            self._create_large_text_file(40),
            self._create_large_text_file(50)
        ]

        results_queue = queue.Queue()
        errors_queue = queue.Queue()

        def load_document(file_path, loader):
            try:
                result = loader.load(file_path)
                results_queue.put((file_path.name, result.metadata.word_count))
            except Exception as e:
                errors_queue.put((file_path.name, str(e)))

        # Create separate loader instances for thread safety
        threads = []
        for file_path in files:
            loader = StreamingDocumentLoader()
            thread = threading.Thread(target=load_document, args=(file_path, loader))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout

        # Check results
        self.assertTrue(errors_queue.empty(), f"Errors during concurrent loading: {list(errors_queue.queue)}")
        self.assertEqual(results_queue.qsize(), len(files), "All files should have been processed")

        # Verify results are reasonable
        while not results_queue.empty():
            filename, word_count = results_queue.get()
            self.assertGreater(word_count, 0, f"File {filename} should have word count > 0")


if __name__ == '__main__':
    logger.info("LocalInsightEngine - Streaming Performance Tests")
    logger.info("=" * 60)
    logger.info("FOCUS: Performance optimization validation")
    logger.info("TARGET: StreamingDocumentLoader vs DocumentLoader")
    logger.info("")

    unittest.main(verbosity=2, buffer=True)