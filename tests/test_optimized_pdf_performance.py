"""
Quick performance test for the optimized PDF loader.
LocalInsightEngine - Optimized PDF Performance Test

Test the new StreamingDocumentLoader with performance metrics.
"""

import sys
import time
import logging
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader

logger = logging.getLogger(__name__)


def test_optimized_pdf_loader():
    """Quick test of the optimized PDF loader."""

    # Change to project root directory
    original_cwd = os.getcwd()
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    try:
        # Path to test PDF
        pdf_path = project_root / "german_sample.pdf"

        if not pdf_path.exists():
            logger.error(f"❌ Test PDF not found: {pdf_path}")
            logger.info("Place a PDF file named 'german_sample.pdf' in the project root.")
            raise unittest.SkipTest(f"Test PDF not found: {pdf_path}")

        file_size_mb = pdf_path.stat().st_size / 1024 / 1024
        logger.info(f"🚀 Testing Optimized PDF Loader")
        logger.info(f"📄 File: {pdf_path.name} ({file_size_mb:.1f} MB)")
        logger.info("=" * 60)

        # Initialize optimized loader
        loader = StreamingDocumentLoader(
            chunk_size=1024*512,  # 512KB chunks
            memory_threshold_mb=50,  # Use streaming for files > 50MB
            enable_streaming=True
        )

        # Get file type info
        file_info = loader.get_file_type_info(pdf_path)
        logger.info(f"📊 File Analysis:")
        logger.info(f"   • Detected type: {file_info['detected_type']}")
        logger.info(f"   • Extension matches: {file_info['matches']}")
        logger.info(f"   • Will use streaming: {file_info['will_use_streaming']}")
        logger.info(f"   • PDF backend: {file_info['pdf_backend']}")
        logger.info("")

        # Load document with timing
        logger.info("⏱️  Loading document...")
        start_time = time.perf_counter()

        document = loader.load(pdf_path)

        end_time = time.perf_counter()
        processing_time = end_time - start_time

        # Add assertions to prevent regressions
        assert document is not None, "Document should not be None"
        assert hasattr(document, 'text_content'), "Document should have text_content attribute"
        assert len(document.text_content) > 0, "Document text_content should not be empty"
        assert hasattr(document, 'metadata'), "Document should have metadata attribute"
        assert document.metadata.page_count > 0, "Document should have at least one page"
        assert isinstance(document.paragraph_mapping, dict), "Paragraph mapping should be a dict"
        assert len(document.paragraph_mapping) > 0, "Document should have at least one paragraph"

        logger.info(f"✅ Document loaded successfully!")
        logger.info(f"   • Processing time: {processing_time:.2f} seconds")
        logger.info(f"   • File format: {document.metadata.file_format}")
        logger.info(f"   • Page count: {document.metadata.page_count}")
        logger.info(f"   • Word count: {document.metadata.word_count:,}")
        logger.info(f"   • Text length: {len(document.text_content):,} characters")
        logger.info(f"   • Paragraphs: {len(document.paragraph_mapping):,}")
        logger.info("")

        # Get processing stats
        stats = loader.get_processing_stats()

        # Add assertions for processing stats
        assert stats is not None, "Processing stats should not be None"
        assert stats.pages_processed > 0, "Should have processed at least one page"
        assert stats.paragraphs_processed > 0, "Should have processed at least one paragraph"
        assert stats.total_chars > 0, "Should have processed at least some characters"
        assert stats.chunks_created >= 0, "Chunks created should be non-negative"

        logger.info(f"📈 Processing Statistics:")
        logger.info(f"   • Pages processed: {stats.pages_processed}")
        logger.info(f"   • Paragraphs processed: {stats.paragraphs_processed:,}")
        logger.info(f"   • Total characters: {stats.total_chars:,}")
        logger.info(f"   • Chunks created: {stats.chunks_created}")
        logger.info("")

        # Performance metrics
        if stats.pages_processed > 0:
            pages_per_second = stats.pages_processed / processing_time
            chars_per_second = stats.total_chars / processing_time
            mb_per_second = file_size_mb / processing_time

            logger.info(f"🏎️  Performance Metrics:")
            logger.info(f"   • Pages per second: {pages_per_second:.1f}")
            logger.info(f"   • Characters per second: {chars_per_second:,.0f}")
            logger.info(f"   • Throughput: {mb_per_second:.1f} MB/second")
            logger.info("")

        # Show sample content
        if len(document.text_content) > 200:
            logger.info(f"📝 Sample Content (first 200 characters):")
            logger.info("-" * 50)
            logger.info(document.text_content[:200] + "...")
            logger.info("")

        # Test specific methods
        if document.page_mapping:
            first_page = min(document.page_mapping.keys())
            first_page_text = document.get_text_by_page(first_page)
            if first_page_text and len(first_page_text) > 100:
                logger.info(f"📖 First Page Sample (100 chars):")
                logger.info("-" * 50)
                logger.info(first_page_text[:100] + "...")
                logger.info("")

        logger.info("✅ Optimized PDF loader test completed successfully!")
        logger.info(f"💡 Recommendation: {'Streaming was used' if file_info['will_use_streaming'] else 'Standard processing was sufficient'}")

    except Exception:
        logger.exception("Error during optimized PDF loader test")
        raise
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    test_optimized_pdf_loader()