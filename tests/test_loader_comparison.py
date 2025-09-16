"""
Performance comparison test between original and optimized document loaders.
LocalInsightEngine - DocumentLoader Performance Comparison

Benchmarks both loaders side-by-side to measure improvements.
"""

import sys
import time
import gc
import psutil
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.data_layer.optimized_document_loader import StreamingDocumentLoader


@dataclass
class LoaderComparison:
    """Comparison results between two loaders."""
    file_path: Path
    file_size_mb: float

    # Original loader results
    original_time: float
    original_memory_mb: float
    original_success: bool
    original_error: str = ""

    # Optimized loader results
    optimized_time: float = 0.0
    optimized_memory_mb: float = 0.0
    optimized_success: bool = False
    optimized_error: str = ""

    # Performance improvements
    time_improvement_percent: float = 0.0
    memory_improvement_percent: float = 0.0

    def __post_init__(self):
        """Calculate improvement percentages."""
        if self.original_success and self.optimized_success:
            if self.original_time > 0:
                self.time_improvement_percent = ((self.original_time - self.optimized_time) / self.original_time) * 100

            if self.original_memory_mb > 0:
                self.memory_improvement_percent = ((self.original_memory_mb - self.optimized_memory_mb) / self.original_memory_mb) * 100


class LoaderPerformanceComparison:
    """Compare performance between original and optimized loaders."""

    def __init__(self):
        self.original_loader = DocumentLoader()
        self.optimized_loader = StreamingDocumentLoader()
        self.process = psutil.Process(os.getpid())
        self.results: List[LoaderComparison] = []

    def _measure_loader_performance(self, loader, file_path: Path) -> Tuple[float, float, bool, str]:
        """
        Measure time and memory usage for a single loader.

        Returns:
            (processing_time, peak_memory_mb, success, error_message)
        """
        gc.collect()
        memory_before = self.process.memory_info().rss / 1024 / 1024

        try:
            start_time = time.perf_counter()

            # Load document
            document = loader.load(file_path)

            end_time = time.perf_counter()
            processing_time = end_time - start_time

            # Measure memory after loading
            memory_after = self.process.memory_info().rss / 1024 / 1024
            memory_usage = memory_after - memory_before

            # Clean up
            del document
            gc.collect()

            return processing_time, memory_usage, True, ""

        except Exception as e:
            gc.collect()
            return 0.0, 0.0, False, str(e)

    def compare_loaders(self, file_path: Path) -> LoaderComparison:
        """Compare both loaders on a single file."""
        file_size_mb = file_path.stat().st_size / 1024 / 1024

        print(f"📊 Comparing loaders on: {file_path.name} ({file_size_mb:.1f} MB)")

        # Test original loader
        print("   🔄 Testing original DocumentLoader...")
        original_time, original_memory, original_success, original_error = \
            self._measure_loader_performance(self.original_loader, file_path)

        if original_success:
            print(f"   ✅ Original: {original_time:.2f}s, {original_memory:.1f}MB")
        else:
            print(f"   ❌ Original failed: {original_error}")

        # Small delay to ensure clean separation
        time.sleep(0.5)
        gc.collect()

        # Test optimized loader
        print("   🚀 Testing StreamingDocumentLoader...")
        optimized_time, optimized_memory, optimized_success, optimized_error = \
            self._measure_loader_performance(self.optimized_loader, file_path)

        if optimized_success:
            print(f"   ✅ Optimized: {optimized_time:.2f}s, {optimized_memory:.1f}MB")
        else:
            print(f"   ❌ Optimized failed: {optimized_error}")

        # Create comparison
        comparison = LoaderComparison(
            file_path=file_path,
            file_size_mb=file_size_mb,
            original_time=original_time,
            original_memory_mb=original_memory,
            original_success=original_success,
            original_error=original_error,
            optimized_time=optimized_time,
            optimized_memory_mb=optimized_memory,
            optimized_success=optimized_success,
            optimized_error=optimized_error
        )

        # Display improvements
        if comparison.original_success and comparison.optimized_success:
            print(f"   📈 Performance improvements:")
            print(f"      ⏱️  Time: {comparison.time_improvement_percent:+.1f}%")
            print(f"      💾 Memory: {comparison.memory_improvement_percent:+.1f}%")

        print()
        self.results.append(comparison)
        return comparison

    def compare_multiple_files(self, file_paths: List[Path]) -> List[LoaderComparison]:
        """Compare both loaders on multiple files."""
        print(f"🔍 Starting comparison of {len(file_paths)} files...")
        print("=" * 80)

        comparisons = []
        for i, file_path in enumerate(file_paths, 1):
            print(f"[{i}/{len(file_paths)}] ", end="")
            comparison = self.compare_loaders(file_path)
            comparisons.append(comparison)

            # Memory cleanup between files
            gc.collect()

        return comparisons

    def generate_comparison_report(self) -> str:
        """Generate detailed comparison report."""
        if not self.results:
            return "No comparison results available."

        # Filter successful comparisons
        successful_comparisons = [
            r for r in self.results
            if r.original_success and r.optimized_success
        ]

        report_lines = [
            "🚀 DocumentLoader Performance Comparison Report",
            "=" * 70,
            f"📋 Test Summary:",
            f"   • Total files tested: {len(self.results)}",
            f"   • Successful comparisons: {len(successful_comparisons)}",
            f"   • Failed tests: {len(self.results) - len(successful_comparisons)}",
            ""
        ]

        if successful_comparisons:
            # Calculate aggregate statistics
            total_original_time = sum(r.original_time for r in successful_comparisons)
            total_optimized_time = sum(r.optimized_time for r in successful_comparisons)

            avg_original_memory = sum(r.original_memory_mb for r in successful_comparisons) / len(successful_comparisons)
            avg_optimized_memory = sum(r.optimized_memory_mb for r in successful_comparisons) / len(successful_comparisons)

            overall_time_improvement = ((total_original_time - total_optimized_time) / total_original_time) * 100
            overall_memory_improvement = ((avg_original_memory - avg_optimized_memory) / avg_original_memory) * 100

            report_lines.extend([
                f"📊 Overall Performance Improvements:",
                f"   ⏱️  Total processing time: {overall_time_improvement:+.1f}%",
                f"   💾 Average memory usage: {overall_memory_improvement:+.1f}%",
                f"   🎯 Speed multiplier: {total_original_time / total_optimized_time:.1f}x",
                ""
            ])

            # Detailed results
            report_lines.extend([
                "📈 Detailed Comparison Results:",
                "-" * 70
            ])

            for r in successful_comparisons:
                speedup = r.original_time / r.optimized_time if r.optimized_time > 0 else 0

                report_lines.extend([
                    f"📄 {r.file_path.name} ({r.file_size_mb:.1f} MB):",
                    f"   Original:  {r.original_time:.2f}s, {r.original_memory_mb:.1f}MB",
                    f"   Optimized: {r.optimized_time:.2f}s, {r.optimized_memory_mb:.1f}MB",
                    f"   Speedup:   {speedup:.1f}x faster, {r.memory_improvement_percent:+.1f}% memory",
                    ""
                ])

        # Backend information
        if hasattr(self.optimized_loader, 'PYMUPDF_AVAILABLE'):
            backend = "PyMuPDF (fitz)" if self.optimized_loader.__class__.__dict__.get('PYMUPDF_AVAILABLE', False) else "PyPDF2"
            report_lines.extend([
                f"🔧 Configuration:",
                f"   • Optimized loader PDF backend: {backend}",
                f"   • Streaming enabled: {self.optimized_loader.enable_streaming}",
                f"   • Memory threshold: {self.optimized_loader.memory_threshold_mb} MB",
                ""
            ])

        # Performance recommendations
        if successful_comparisons:
            report_lines.extend([
                "💡 Performance Analysis:",
                "-" * 70
            ])

            if overall_time_improvement > 20:
                report_lines.append("✅ Significant processing speed improvements detected!")

            if overall_memory_improvement > 15:
                report_lines.append("✅ Substantial memory usage reduction achieved!")

            large_files = [r for r in successful_comparisons if r.file_size_mb > 10]
            if large_files:
                large_file_time_improvement = sum(r.time_improvement_percent for r in large_files) / len(large_files)
                report_lines.append(f"📈 Large files (>10MB) show {large_file_time_improvement:.1f}% average improvement")

            # Failure analysis
            failed_results = [r for r in self.results if not (r.original_success and r.optimized_success)]
            if failed_results:
                report_lines.extend([
                    "",
                    "❌ Failed Tests:",
                    "-" * 70
                ])

                for r in failed_results:
                    if not r.original_success and not r.optimized_success:
                        report_lines.append(f"❌ {r.file_path.name}: Both loaders failed")
                    elif not r.original_success:
                        report_lines.append(f"⚠️  {r.file_path.name}: Original failed, optimized succeeded")
                    else:
                        report_lines.append(f"⚠️  {r.file_path.name}: Original succeeded, optimized failed")

        return "\n".join(report_lines)

    def save_comparison_report(self, output_path: Path):
        """Save comparison report to file."""
        report = self.generate_comparison_report()
        output_path.write_text(report, encoding='utf-8')
        print(f"📊 Comparison report saved to: {output_path}")


def run_loader_comparison():
    """Run the loader comparison test."""
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Find test PDF files
    test_pdfs = []

    potential_pdfs = [
        project_root / "german_sample.pdf",
        project_root / "test_samples" / "sample.pdf",
        project_root / "samples" / "*.pdf"
    ]

    for pdf_pattern in potential_pdfs:
        if pdf_pattern.exists() and pdf_pattern.is_file():
            test_pdfs.append(pdf_pattern)
        elif '*' in str(pdf_pattern):
            test_pdfs.extend(pdf_pattern.parent.glob(pdf_pattern.name))

    if not test_pdfs:
        print("⚠️  No test PDF files found.")
        print("Place PDF files in project root or test_samples/ directory.")
        return

    # Run comparison
    comparator = LoaderPerformanceComparison()
    comparisons = comparator.compare_multiple_files(test_pdfs)

    # Generate and display report
    print("=" * 80)
    print(comparator.generate_comparison_report())

    # Save report
    report_path = project_root / "loader_comparison_report.txt"
    comparator.save_comparison_report(report_path)

    return comparator


if __name__ == "__main__":
    run_loader_comparison()