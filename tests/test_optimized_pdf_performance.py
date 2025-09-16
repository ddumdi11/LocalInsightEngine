"""
Quick performance test for the optimized PDF loader.
LocalInsightEngine - Optimized PDF Performance Test

Test the new StreamingDocumentLoader with performance metrics.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader


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
            print(f"❌ Test PDF not found: {pdf_path}")
            print("Place a PDF file named 'german_sample.pdf' in the project root.")
            return

        file_size_mb = pdf_path.stat().st_size / 1024 / 1024
        print(f"🚀 Testing Optimized PDF Loader")
        print(f"📄 File: {pdf_path.name} ({file_size_mb:.1f} MB)")
        print("=" * 60)

        # Initialize optimized loader
        loader = StreamingDocumentLoader(
            chunk_size=1024*512,  # 512KB chunks
            memory_threshold_mb=50,  # Use streaming for files > 50MB
            enable_streaming=True
        )

        # Get file type info
        file_info = loader.get_file_type_info(pdf_path)
        print(f"📊 File Analysis:")
        print(f"   • Detected type: {file_info['detected_type']}")
        print(f"   • Extension matches: {file_info['matches']}")
        print(f"   • Will use streaming: {file_info['will_use_streaming']}")
        print(f"   • PDF backend: {file_info['pdf_backend']}")
        print()

        # Load document with timing
        print("⏱️  Loading document...")
        start_time = time.perf_counter()

        document = loader.load(pdf_path)

        end_time = time.perf_counter()
        processing_time = end_time - start_time

        print(f"✅ Document loaded successfully!")
        print(f"   • Processing time: {processing_time:.2f} seconds")
        print(f"   • File format: {document.metadata.file_format}")
        print(f"   • Page count: {document.metadata.page_count}")
        print(f"   • Word count: {document.metadata.word_count:,}")
        print(f"   • Text length: {len(document.text_content):,} characters")
        print(f"   • Paragraphs: {len(document.paragraph_mapping):,}")
        print()

        # Get processing stats
        stats = loader.get_processing_stats()
        print(f"📈 Processing Statistics:")
        print(f"   • Pages processed: {stats.pages_processed}")
        print(f"   • Paragraphs processed: {stats.paragraphs_processed:,}")
        print(f"   • Total characters: {stats.total_chars:,}")
        print(f"   • Chunks created: {stats.chunks_created}")
        print()

        # Performance metrics
        if stats.pages_processed > 0:
            pages_per_second = stats.pages_processed / processing_time
            chars_per_second = stats.total_chars / processing_time
            mb_per_second = file_size_mb / processing_time

            print(f"🏎️  Performance Metrics:")
            print(f"   • Pages per second: {pages_per_second:.1f}")
            print(f"   • Characters per second: {chars_per_second:,.0f}")
            print(f"   • Throughput: {mb_per_second:.1f} MB/second")
            print()

        # Show sample content
        if len(document.text_content) > 200:
            print(f"📝 Sample Content (first 200 characters):")
            print("-" * 50)
            print(document.text_content[:200] + "...")
            print()

        # Test specific methods
        if document.page_mapping:
            first_page = min(document.page_mapping.keys())
            first_page_text = document.get_text_by_page(first_page)
            if first_page_text and len(first_page_text) > 100:
                print(f"📖 First Page Sample (100 chars):")
                print("-" * 50)
                print(first_page_text[:100] + "...")
                print()

        print("✅ Optimized PDF loader test completed successfully!")
        print(f"💡 Recommendation: {'Streaming was used' if file_info['will_use_streaming'] else 'Standard processing was sufficient'}")

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    test_optimized_pdf_loader()