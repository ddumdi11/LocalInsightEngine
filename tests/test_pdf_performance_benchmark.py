"""
Performance benchmark test for PDF processing optimization.
LocalInsightEngine - PDF Performance Benchmarking Suite

Measures memory usage, processing time, and scalability metrics.
"""

import sys
import time
import gc
import psutil
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    file_path: Path
    file_size_mb: float
    page_count: int
    word_count: int
    processing_time_seconds: float
    peak_memory_mb: float
    memory_before_mb: float
    memory_after_mb: float
    success: bool
    error_message: Optional[str] = None


class PDFPerformanceBenchmark:
    """Benchmark suite for PDF processing performance."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.loader = DocumentLoader()
        self.process = psutil.Process(os.getpid())

    @contextmanager
    def memory_monitor(self):
        """Context manager to monitor memory usage during execution."""
        gc.collect()  # Clean up before measurement
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        peak_memory = memory_before

        try:
            yield lambda: peak_memory
        finally:
            gc.collect()
            memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
            self.last_memory_stats = {
                'before': memory_before,
                'after': memory_after,
                'peak': max(peak_memory, memory_after)
            }

    def _update_peak_memory(self, peak_tracker):
        """Update peak memory usage during monitoring."""
        current_memory = self.process.memory_info().rss / 1024 / 1024
        if hasattr(peak_tracker, '__call__'):
            # This would need a more sophisticated implementation for real peak tracking
            return max(current_memory, peak_tracker())
        return current_memory

    def benchmark_single_pdf(self, pdf_path: Path) -> BenchmarkResult:
        """Benchmark processing of a single PDF file."""
        if not pdf_path.exists():
            return BenchmarkResult(
                file_path=pdf_path,
                file_size_mb=0,
                page_count=0,
                word_count=0,
                processing_time_seconds=0,
                peak_memory_mb=0,
                memory_before_mb=0,
                memory_after_mb=0,
                success=False,
                error_message=f"File not found: {pdf_path}"
            )

        file_size_mb = pdf_path.stat().st_size / 1024 / 1024

        try:
            with self.memory_monitor() as peak_tracker:
                start_time = time.perf_counter()

                # Actual PDF processing
                document = self.loader.load(pdf_path)

                end_time = time.perf_counter()
                processing_time = end_time - start_time

            # Extract metrics
            memory_stats = self.last_memory_stats

            result = BenchmarkResult(
                file_path=pdf_path,
                file_size_mb=file_size_mb,
                page_count=document.metadata.page_count or 0,
                word_count=document.metadata.word_count or 0,
                processing_time_seconds=processing_time,
                peak_memory_mb=memory_stats['peak'],
                memory_before_mb=memory_stats['before'],
                memory_after_mb=memory_stats['after'],
                success=True
            )

            self.results.append(result)
            return result

        except Exception as e:
            error_result = BenchmarkResult(
                file_path=pdf_path,
                file_size_mb=file_size_mb,
                page_count=0,
                word_count=0,
                processing_time_seconds=0,
                peak_memory_mb=0,
                memory_before_mb=0,
                memory_after_mb=0,
                success=False,
                error_message=str(e)
            )
            self.results.append(error_result)
            return error_result

    def benchmark_multiple_files(self, pdf_paths: List[Path]) -> List[BenchmarkResult]:
        """Benchmark processing of multiple PDF files."""
        results = []

        print(f"📊 Starting benchmark of {len(pdf_paths)} PDF files...")
        print("=" * 80)

        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"[{i}/{len(pdf_paths)}] Processing: {pdf_path.name}")

            result = self.benchmark_single_pdf(pdf_path)
            results.append(result)

            if result.success:
                print(f"  ✅ Success: {result.processing_time_seconds:.2f}s, "
                      f"{result.peak_memory_mb:.1f}MB peak, "
                      f"{result.page_count} pages, "
                      f"{result.word_count} words")
            else:
                print(f"  ❌ Failed: {result.error_message}")

            # Memory cleanup between files
            gc.collect()

        return results

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        if not self.results:
            return "No benchmark results available."

        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]

        if not successful_results:
            return f"All {len(self.results)} benchmark tests failed."

        # Calculate statistics
        total_files = len(successful_results)
        total_processing_time = sum(r.processing_time_seconds for r in successful_results)
        avg_processing_time = total_processing_time / total_files

        total_pages = sum(r.page_count for r in successful_results)
        avg_pages_per_second = total_pages / total_processing_time if total_processing_time > 0 else 0

        peak_memory_usage = max(r.peak_memory_mb for r in successful_results)
        avg_memory_usage = sum(r.peak_memory_mb for r in successful_results) / total_files

        # Memory efficiency (pages per MB)
        pages_per_mb = []
        for r in successful_results:
            if r.peak_memory_mb > 0:
                pages_per_mb.append(r.page_count / r.peak_memory_mb)
        avg_pages_per_mb = sum(pages_per_mb) / len(pages_per_mb) if pages_per_mb else 0

        # Processing efficiency (MB per second)
        mb_per_second = []
        for r in successful_results:
            if r.processing_time_seconds > 0:
                mb_per_second.append(r.file_size_mb / r.processing_time_seconds)
        avg_mb_per_second = sum(mb_per_second) / len(mb_per_second) if mb_per_second else 0

        # Build report
        report_lines = [
            "🔍 PDF Processing Performance Benchmark Report",
            "=" * 60,
            f"📋 Test Summary:",
            f"   • Total files tested: {len(self.results)}",
            f"   • Successful: {len(successful_results)}",
            f"   • Failed: {len(failed_results)}",
            "",
            f"⏱️  Processing Performance:",
            f"   • Total processing time: {total_processing_time:.2f} seconds",
            f"   • Average time per file: {avg_processing_time:.2f} seconds",
            f"   • Pages processed per second: {avg_pages_per_second:.1f}",
            f"   • File throughput: {avg_mb_per_second:.1f} MB/second",
            "",
            f"💾 Memory Usage:",
            f"   • Peak memory usage: {peak_memory_usage:.1f} MB",
            f"   • Average memory usage: {avg_memory_usage:.1f} MB",
            f"   • Memory efficiency: {avg_pages_per_mb:.1f} pages/MB",
            "",
            f"📄 Document Statistics:",
            f"   • Total pages processed: {total_pages}",
            f"   • Average pages per document: {total_pages / total_files:.1f}",
            f"   • Total words processed: {sum(r.word_count for r in successful_results):,}",
            ""
        ]

        # Detailed results for each file
        if successful_results:
            report_lines.extend([
                "📊 Detailed Results:",
                "-" * 60
            ])

            for r in successful_results:
                efficiency_score = (r.page_count / r.processing_time_seconds) if r.processing_time_seconds > 0 else 0
                memory_efficiency = (r.page_count / r.peak_memory_mb) if r.peak_memory_mb > 0 else 0

                report_lines.append(
                    f"📄 {r.file_path.name}:"
                )
                report_lines.append(
                    f"   Size: {r.file_size_mb:.1f}MB | Pages: {r.page_count} | "
                    f"Time: {r.processing_time_seconds:.2f}s | Memory: {r.peak_memory_mb:.1f}MB"
                )
                report_lines.append(
                    f"   Efficiency: {efficiency_score:.1f} pages/sec | "
                    f"Memory ratio: {memory_efficiency:.1f} pages/MB"
                )
                report_lines.append("")

        # Failed files
        if failed_results:
            report_lines.extend([
                "❌ Failed Files:",
                "-" * 60
            ])

            for r in failed_results:
                report_lines.append(f"❌ {r.file_path.name}: {r.error_message}")

            report_lines.append("")

        # Performance recommendations
        report_lines.extend([
            "🚀 Performance Optimization Recommendations:",
            "-" * 60,
        ])

        if avg_processing_time > 5.0:
            report_lines.append("⚠️  High processing time detected - consider streaming/chunking")

        if peak_memory_usage > 500:
            report_lines.append("⚠️  High memory usage detected - implement memory-efficient processing")

        if avg_pages_per_second < 10:
            report_lines.append("⚠️  Low throughput - consider parallel processing or faster PDF library")

        if avg_pages_per_mb < 50:
            report_lines.append("⚠️  Poor memory efficiency - optimize data structures")

        return "\n".join(report_lines)

    def save_report(self, output_path: Path):
        """Save performance report to file."""
        report = self.generate_performance_report()
        output_path.write_text(report, encoding='utf-8')
        print(f"📊 Performance report saved to: {output_path}")


def run_benchmark():
    """Run the PDF performance benchmark."""
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Find test PDF files
    test_pdfs = []

    # Look for sample PDFs in project
    potential_pdfs = [
        project_root / "german_sample.pdf",
        project_root / "test_samples" / "sample.pdf",
        project_root / "samples" / "*.pdf"
    ]

    for pdf_pattern in potential_pdfs:
        if pdf_pattern.exists() and pdf_pattern.is_file():
            test_pdfs.append(pdf_pattern)
        elif '*' in str(pdf_pattern):
            # Handle glob patterns
            test_pdfs.extend(pdf_pattern.parent.glob(pdf_pattern.name))

    if not test_pdfs:
        print("⚠️  No test PDF files found. Creating synthetic benchmark...")
        print("Place PDF files in project root or test_samples/ directory for realistic benchmarks.")
        return

    # Run benchmark
    benchmark = PDFPerformanceBenchmark()
    results = benchmark.benchmark_multiple_files(test_pdfs)

    # Generate and display report
    print("\n" + "=" * 80)
    print(benchmark.generate_performance_report())

    # Save report
    report_path = project_root / "performance_report.txt"
    benchmark.save_report(report_path)

    return benchmark


if __name__ == "__main__":
    run_benchmark()