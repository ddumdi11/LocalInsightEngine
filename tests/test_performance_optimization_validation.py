"""
Performance Optimization Validation Tests for LocalInsightEngine.
LocalInsightEngine v0.1.1 - Validation Tests for Original vs Optimized Implementations

FOCUS: Validate that optimized implementations maintain functionality while improving performance
COVERAGE: Original vs Optimized DocumentLoader, Memory Usage, Processing Speed, Correctness
"""

import sys
import unittest
import tempfile
import time
import gc
import psutil
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    processing_time_seconds: float
    peak_memory_mb: float
    memory_delta_mb: float
    success: bool
    error_message: Optional[str] = None
    result_hash: Optional[str] = None  # For content validation


class PerformanceOptimizationValidator:
    """Validator for comparing original vs optimized implementations."""

    def __init__(self):
        self.original_loader = DocumentLoader()
        self.optimized_loader = StreamingDocumentLoader()
        self.process = psutil.Process(os.getpid())
    def measure_performance(self, loader, document_path: Path) -> PerformanceMetrics:
        """Measure performance metrics for a loader implementation."""
        gc.collect()  # Clean up before measurement
        initial_memory = self.process.memory_info().rss / 1024 / 1024

        try:
            start_time = time.perf_counter()

            # Load document
            document = loader.load(document_path)

            end_time = time.perf_counter()
            processing_time = end_time - start_time

            # Measure peak memory
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            memory_delta = peak_memory - initial_memory

            # Create content hash for validation
            import hashlib
            content_hash = hashlib.md5(document.text_content.encode()).hexdigest()

            return PerformanceMetrics(
                processing_time_seconds=processing_time,
                peak_memory_mb=peak_memory,
                memory_delta_mb=memory_delta,
                success=True,
                result_hash=content_hash
            )

        except Exception as e:
            final_memory = self.process.memory_info().rss / 1024 / 1024
            return PerformanceMetrics(
                processing_time_seconds=0,
                peak_memory_mb=final_memory,
                memory_delta_mb=final_memory - initial_memory,
                success=False,
                error_message=str(e)
            )

    def compare_implementations(self, document_path: Path) -> Dict[str, PerformanceMetrics]:
        """Compare original vs optimized implementation performance."""
        results = {}

        logger.info(f"Comparing implementations for: {document_path.name}")

        # Test original implementation
        logger.info("  Testing original implementation...")
        results['original'] = self.measure_performance(self.original_loader, document_path)

        # Clean up between tests
        gc.collect()
        time.sleep(0.1)

        # Test optimized implementation
        logger.info("  Testing optimized implementation...")
        results['optimized'] = self.measure_performance(self.optimized_loader, document_path)

        return results

    def validate_correctness(self, results: Dict[str, PerformanceMetrics]) -> bool:
        """Validate that both implementations produce the same results."""
        if not (results['original'].success and results['optimized'].success):
            return False

        # Compare content hashes
        return results['original'].result_hash == results['optimized'].result_hash

    def analyze_performance_improvement(self, results: Dict[str, PerformanceMetrics]) -> Dict[str, float]:
        """Analyze performance improvements between implementations."""
        if not (results['original'].success and results['optimized'].success):
            return {}

        original = results['original']
        optimized = results['optimized']

        speed_improvement = (original.processing_time_seconds - optimized.processing_time_seconds) / original.processing_time_seconds * 100
        memory_improvement = (original.memory_delta_mb - optimized.memory_delta_mb) / original.memory_delta_mb * 100 if original.memory_delta_mb > 0 else 0

        return {
            'speed_improvement_percent': speed_improvement,
            'memory_improvement_percent': memory_improvement,
            'original_time': original.processing_time_seconds,
            'optimized_time': optimized.processing_time_seconds,
            'original_memory': original.memory_delta_mb,
            'optimized_memory': optimized.memory_delta_mb
        }


class TestPerformanceOptimization(unittest.TestCase):
    """Test suite for validating performance optimizations."""

    def setUp(self):
        self.validator = PerformanceOptimizationValidator()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def create_test_pdf_content(self, pages: int = 5, words_per_page: int = 500) -> Path:
        """Create a test PDF-like content file for testing."""
        # Since we can't easily create real PDFs, create text files that simulate PDF content
        content_lines = []
        for page in range(pages):
            content_lines.append(f"=== Page {page + 1} ===")
            for para in range(3):  # 3 paragraphs per page
                words = [f"word{i}_{page}_{para}" for i in range(words_per_page // 3)]
                content_lines.append(" ".join(words))
                content_lines.append("")  # Empty line between paragraphs

        test_file = self.test_dir / f"test_content_{pages}pages.txt"
        test_file.write_text("\n".join(content_lines), encoding='utf-8')
        return test_file

    def test_small_document_optimization(self):
        """Test optimization performance on small documents."""
        logger.info("\n=== Testing Small Document Optimization ===")

        # Create small test document
        small_doc = self.create_test_pdf_content(pages=2, words_per_page=100)

        # Compare implementations
        results = self.validator.compare_implementations(small_doc)

        # Validate correctness
        correctness_valid = self.validator.validate_correctness(results)
        self.assertTrue(correctness_valid, "Optimized implementation produces different results than original")

        # Analyze performance
        if results['original'].success and results['optimized'].success:
            improvements = self.validator.analyze_performance_improvement(results)

            logger.info(f"  Original time: {improvements['original_time']:.4f}s")
            logger.info(f"  Optimized time: {improvements['optimized_time']:.4f}s")
            logger.info(f"  Speed improvement: {improvements['speed_improvement_percent']:.1f}%")
            logger.info(f"  Memory improvement: {improvements['memory_improvement_percent']:.1f}%")

            # For small documents, optimization might not show significant gains
            # But it should not be significantly worse
            self.assertGreaterEqual(improvements['speed_improvement_percent'], -50,
                                   "Optimized implementation significantly slower than original")

    def test_medium_document_optimization(self):
        """Test optimization performance on medium-sized documents."""
        logger.info("\n=== Testing Medium Document Optimization ===")

        # Create medium test document
        medium_doc = self.create_test_pdf_content(pages=10, words_per_page=1000)

        # Compare implementations
        results = self.validator.compare_implementations(medium_doc)

        # Validate correctness
        correctness_valid = self.validator.validate_correctness(results)
        self.assertTrue(correctness_valid, "Optimized implementation produces different results than original")

        # Analyze performance
        if results['original'].success and results['optimized'].success:
            improvements = self.validator.analyze_performance_improvement(results)

            logger.info(f"  Original time: {improvements['original_time']:.4f}s")
            logger.info(f"  Optimized time: {improvements['optimized_time']:.4f}s")
            logger.info(f"  Speed improvement: {improvements['speed_improvement_percent']:.1f}%")
            logger.info(f"  Memory improvement: {improvements['memory_improvement_percent']:.1f}%")

            # Medium documents should show some improvement
            self.assertGreaterEqual(improvements['speed_improvement_percent'], -10,
                                   "Optimized implementation slower than original for medium documents")

    def test_large_document_optimization(self):
        """Test optimization performance on large documents."""
        logger.info("\n=== Testing Large Document Optimization ===")

        # Create large test document
        large_doc = self.create_test_pdf_content(pages=50, words_per_page=2000)

        # Compare implementations
        results = self.validator.compare_implementations(large_doc)

        # Validate correctness
        correctness_valid = self.validator.validate_correctness(results)
        self.assertTrue(correctness_valid, "Optimized implementation produces different results than original")

        # Analyze performance
        if results['original'].success and results['optimized'].success:
            improvements = self.validator.analyze_performance_improvement(results)

            logger.info(f"  Original time: {improvements['original_time']:.4f}s")
            logger.info(f"  Optimized time: {improvements['optimized_time']:.4f}s")
            logger.info(f"  Speed improvement: {improvements['speed_improvement_percent']:.1f}%")
            logger.info(f"  Memory improvement: {improvements['memory_improvement_percent']:.1f}%")

            # Large documents should show significant improvement
            self.assertGreater(improvements['speed_improvement_percent'], 0,
                              "No speed improvement for large documents")

    def test_memory_efficiency_optimization(self):
        """Test memory efficiency improvements."""
        logger.info("\n=== Testing Memory Efficiency ===")

        # Create document designed to test memory usage
        memory_test_doc = self.create_test_pdf_content(pages=20, words_per_page=5000)

        results = self.validator.compare_implementations(memory_test_doc)

        if results['original'].success and results['optimized'].success:
            original_memory = results['original'].memory_delta_mb
            optimized_memory = results['optimized'].memory_delta_mb

            logger.info(f"  Original memory usage: {original_memory:.2f}MB")
            logger.info(f"  Optimized memory usage: {optimized_memory:.2f}MB")

            # Optimized version should use same or less memory
            memory_ratio = optimized_memory / original_memory if original_memory > 0 else 1
            self.assertLessEqual(memory_ratio, 1.1,  # Allow 10% margin
                                f"Optimized implementation uses significantly more memory: {memory_ratio:.2f}x")

    def test_concurrent_processing_optimization(self):
        """Test optimization performance under concurrent load."""
        logger.info("\n=== Testing Concurrent Processing ===")

        # Create multiple test documents
        test_docs = []
        for i in range(3):
            doc = self.create_test_pdf_content(pages=5, words_per_page=500)
            doc = doc.rename(self.test_dir / f"concurrent_test_{i}.txt")
            test_docs.append(doc)

        def process_with_loader(loader, docs):
            """Process documents with given loader."""
            start_time = time.perf_counter()
            success_count = 0

            for doc in docs:
                try:
                    result = loader.load(doc)
                    if result:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error processing {doc}: {e}")

            end_time = time.perf_counter()
            return end_time - start_time, success_count

        # Test original implementation
        original_time, original_success = process_with_loader(self.validator.original_loader, test_docs)

        # Test optimized implementation
        optimized_time, optimized_success = process_with_loader(self.validator.optimized_loader, test_docs)

        logger.info(f"  Original: {original_time:.4f}s ({original_success} successful)")
        logger.info(f"  Optimized: {optimized_time:.4f}s ({optimized_success} successful)")

        # Both should process all documents successfully
        self.assertEqual(original_success, len(test_docs), "Original implementation failed some documents")
        self.assertEqual(optimized_success, len(test_docs), "Optimized implementation failed some documents")

        # Optimized should be faster or at least not significantly slower
        speed_ratio = optimized_time / original_time if original_time > 0 else 1
        self.assertLessEqual(speed_ratio, 1.2,  # Allow 20% margin
                            f"Optimized implementation significantly slower: {speed_ratio:.2f}x")

    def test_error_handling_consistency(self):
        """Test that optimization maintains error handling behavior."""
        logger.info("\n=== Testing Error Handling Consistency ===")

        # Test with non-existent file
        non_existent = self.test_dir / "does_not_exist.txt"

        # Both implementations should handle missing files the same way
        original_error = None
        optimized_error = None

        try:
            self.validator.original_loader.load(non_existent)
        except Exception as e:
            original_error = type(e)

        try:
            self.validator.optimized_loader.load(non_existent)
        except Exception as e:
            optimized_error = type(e)

        self.assertEqual(original_error, optimized_error,
                        "Optimized implementation has different error handling behavior")

    def test_output_format_consistency(self):
        """Test that optimization maintains output format consistency."""
        logger.info("\n=== Testing Output Format Consistency ===")

        # Create test document
        test_doc = self.create_test_pdf_content(pages=3, words_per_page=200)

        # Load with both implementations
        original_result = self.validator.original_loader.load(test_doc)
        optimized_result = self.validator.optimized_loader.load(test_doc)

        # Compare document structure
        self.assertEqual(type(original_result), type(optimized_result),
                        "Different return types between implementations")

        # Compare metadata structure
        self.assertEqual(type(original_result.metadata), type(optimized_result.metadata),
                        "Different metadata types between implementations")

        # Compare content (should be identical)
        self.assertEqual(original_result.text_content, optimized_result.text_content,
                        "Different text content between implementations")

        # Compare mapping structures
        self.assertEqual(len(original_result.page_mapping), len(optimized_result.page_mapping),
                        "Different page mapping lengths between implementations")

        logger.info("  ✓ Output format consistency validated")


class TestOptimizationRegression(unittest.TestCase):
    """Regression tests to ensure optimizations don't break existing functionality."""

    def setUp(self):
        self.original_loader = DocumentLoader()
        self.optimized_loader = OptimizedDocumentLoader()

    def test_file_type_detection_regression(self):
        """Test that file type detection still works correctly."""
        # Test with various file extensions
        test_files = {
            'test.txt': 'txt',
            'test.pdf': 'pdf',
            'test.docx': 'docx',
            'test.epub': 'epub'
        }

        for filename, expected_type in test_files.items():
            with tempfile.NamedTemporaryFile(suffix=f".{expected_type}", delete=False) as f:
                test_path = Path(f.name)

            try:
                # Both implementations should handle supported formats
                self.assertTrue(self.original_loader._is_supported_format(test_path))
                self.assertTrue(self.optimized_loader._is_supported_format(test_path))

                # Format detection should be consistent
                original_format = self.original_loader._get_file_format(test_path)
                optimized_format = self.optimized_loader._get_file_format(test_path)

                self.assertEqual(original_format, optimized_format,
                               f"Inconsistent format detection for {filename}")

            finally:
                if test_path.exists():
                    test_path.unlink()

    def test_metadata_extraction_regression(self):
        """Test that metadata extraction remains consistent."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Test content for metadata extraction")
            test_file = Path(f.name)

        try:
            original_doc = self.original_loader.load(test_file)
            optimized_doc = self.optimized_loader.load(test_file)

            # Compare key metadata fields
            self.assertEqual(original_doc.metadata.file_format, optimized_doc.metadata.file_format)
            self.assertEqual(original_doc.metadata.file_size, optimized_doc.metadata.file_size)
            self.assertEqual(original_doc.metadata.word_count, optimized_doc.metadata.word_count)

        finally:
            test_file.unlink()


if __name__ == '__main__':
    logger.info("LocalInsightEngine - Performance Optimization Validation Tests")
    logger.info("=" * 70)
    logger.info("VALIDATION: Original vs Optimized DocumentLoader Performance & Correctness")
    logger.info("METRICS: Processing Speed, Memory Usage, Output Consistency")
    logger.info("")

    unittest.main(verbosity=2, buffer=True)