"""
Comprehensive Test Suite Runner for LocalInsightEngine.
LocalInsightEngine v0.1.1 - Master Test Orchestrator for Complete Coverage

SCOPE: Orchestrates all test suites for comprehensive coverage validation
OUTPUT: Detailed coverage report with performance metrics and edge case validation
"""

import sys
import unittest
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class TestSuiteResult:
    """Results from running a single test suite."""
    suite_name: str
    tests_run: int
    failures: int
    errors: int
    skipped: int
    execution_time: float
    success_rate: float = field(init=False)

    def __post_init__(self):
        if self.tests_run > 0:
            self.success_rate = ((self.tests_run - self.failures - self.errors) / self.tests_run) * 100
        else:
            self.success_rate = 0.0


@dataclass
class CoverageReport:
    """Code coverage analysis results."""
    total_coverage: float
    module_coverage: Dict[str, float]
    missing_lines: Dict[str, List[int]]
    critical_paths_covered: float


class ComprehensiveTestRunner:
    """Master test runner for all LocalInsightEngine test suites."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.results: List[TestSuiteResult] = []

        # Define test suites in order of execution
        self.test_suites = [
            ("Unit Tests", "test_unit_tests.py"),
            ("Edge Cases", "test_edge_cases_comprehensive.py"),
            ("Performance Optimization", "test_performance_optimization_validation.py"),
            ("Critical Paths Coverage", "test_critical_paths_coverage.py"),
            ("Anonymization Proof", "test_anonymization_proof.py"),
            ("PDF Performance Benchmark", "test_pdf_performance_benchmark.py"),
            ("Multi-format Support", "test_multiformat.py"),
            ("File Detection", "test_file_detection.py")
        ]

    def run_single_test_suite(self, suite_name: str, test_file: str) -> TestSuiteResult:
        """Run a single test suite and capture results."""
        print(f"\n{'='*60}")
        print(f"Running Test Suite: {suite_name}")
        print(f"File: {test_file}")
        print(f"{'='*60}")

        test_path = self.tests_dir / test_file

        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
            return TestSuiteResult(
                suite_name=suite_name,
                tests_run=0,
                failures=0,
                errors=1,
                skipped=0,
                execution_time=0.0
            )

        start_time = time.perf_counter()

        try:
            # Import and run the test module
            sys.path.insert(0, str(self.tests_dir))

            # Import the test module dynamically
            module_name = test_file.replace('.py', '')

            # Remove existing module if already imported
            if module_name in sys.modules:
                del sys.modules[module_name]

            test_module = __import__(module_name)

            # Create test loader and suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)

            # Run tests with custom result collector
            test_result = unittest.TestResult()
            suite.run(test_result)

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # Extract results
            result = TestSuiteResult(
                suite_name=suite_name,
                tests_run=test_result.testsRun,
                failures=len(test_result.failures),
                errors=len(test_result.errors),
                skipped=len(test_result.skipped),
                execution_time=execution_time
            )

            # Print summary
            print(f"✅ Tests run: {result.tests_run}")
            print(f"❌ Failures: {result.failures}")
            print(f"💥 Errors: {result.errors}")
            print(f"⏭️  Skipped: {result.skipped}")
            print(f"⏱️  Time: {result.execution_time:.2f}s")
            print(f"📊 Success rate: {result.success_rate:.1f}%")

            # Print failure details if any
            if test_result.failures:
                print(f"\n❌ FAILURES:")
                for test, traceback in test_result.failures:
                    print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")

            if test_result.errors:
                print(f"\n💥 ERRORS:")
                for test, traceback in test_result.errors:
                    print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")

            return result

        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            print(f"💥 Failed to run test suite: {e}")

            return TestSuiteResult(
                suite_name=suite_name,
                tests_run=0,
                failures=0,
                errors=1,
                skipped=0,
                execution_time=execution_time
            )

    def run_coverage_analysis(self) -> Optional[CoverageReport]:
        """Run code coverage analysis if tools are available."""
        print(f"\n{'='*60}")
        print("Running Code Coverage Analysis")
        print(f"{'='*60}")

        try:
            # Try to run coverage analysis
            coverage_cmd = [
                sys.executable, "-m", "pytest",
                "--cov=src",
                "--cov-report=json",
                "--cov-report=term-missing",
                str(self.tests_dir)
            ]

            # First check if pytest and coverage are available
            try:
                subprocess.run([sys.executable, "-m", "pytest", "--version"],
                             capture_output=True, check=True, cwd=self.project_root)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  pytest not available - skipping coverage analysis")
                return None

            # Run coverage
            result = subprocess.run(
                coverage_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )

            print("Coverage analysis output:")
            print(result.stdout)

            if result.stderr:
                print("Coverage warnings/errors:")
                print(result.stderr)

            # Try to parse coverage report
            coverage_json_path = self.project_root / "coverage.json"
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)

                # Extract key metrics
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)

                module_coverage = {}
                missing_lines = {}

                for filename, file_data in coverage_data.get('files', {}).items():
                    if 'src/local_insight_engine' in filename:
                        module_name = Path(filename).name
                        module_coverage[module_name] = file_data.get('summary', {}).get('percent_covered', 0.0)
                        missing_lines[module_name] = file_data.get('missing_lines', [])

                # Calculate critical paths coverage (estimate)
                critical_modules = [
                    'document_loader.py',
                    'spacy_entity_extractor.py',
                    'text_processor.py',
                    'claude_client.py'
                ]

                critical_coverage_sum = sum(
                    module_coverage.get(module, 0) for module in critical_modules
                )
                critical_paths_covered = critical_coverage_sum / len(critical_modules) if critical_modules else 0

                return CoverageReport(
                    total_coverage=total_coverage,
                    module_coverage=module_coverage,
                    missing_lines=missing_lines,
                    critical_paths_covered=critical_paths_covered
                )

        except subprocess.TimeoutExpired:
            print("⚠️  Coverage analysis timed out")
        except Exception as e:
            print(f"⚠️  Coverage analysis failed: {e}")

        return None

    def generate_comprehensive_report(self, coverage_report: Optional[CoverageReport] = None) -> str:
        """Generate a comprehensive test report."""
        report_lines = [
            "🔍 LOCALINSIGHTENGINE - COMPREHENSIVE TEST REPORT",
            "=" * 80,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project: LocalInsightEngine v0.1.1",
            "",
            "📋 TEST SUITE SUMMARY:",
            "-" * 40
        ]

        total_tests = sum(r.tests_run for r in self.results)
        total_failures = sum(r.failures for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        total_time = sum(r.execution_time for r in self.results)

        overall_success_rate = 0
        if total_tests > 0:
            overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100

        report_lines.extend([
            f"Total Test Suites: {len(self.results)}",
            f"Total Tests Run: {total_tests}",
            f"Total Failures: {total_failures}",
            f"Total Errors: {total_errors}",
            f"Total Skipped: {total_skipped}",
            f"Total Execution Time: {total_time:.2f}s",
            f"Overall Success Rate: {overall_success_rate:.1f}%",
            ""
        ])

        # Individual suite results
        report_lines.extend([
            "📊 INDIVIDUAL SUITE RESULTS:",
            "-" * 40
        ])

        for result in self.results:
            status_icon = "✅" if result.failures == 0 and result.errors == 0 else "❌"
            report_lines.append(
                f"{status_icon} {result.suite_name}:"
            )
            report_lines.append(
                f"   Tests: {result.tests_run} | Failures: {result.failures} | "
                f"Errors: {result.errors} | Time: {result.execution_time:.2f}s | "
                f"Success: {result.success_rate:.1f}%"
            )

        report_lines.append("")

        # Coverage analysis
        if coverage_report:
            report_lines.extend([
                "📈 CODE COVERAGE ANALYSIS:",
                "-" * 40,
                f"Total Coverage: {coverage_report.total_coverage:.1f}%",
                f"Critical Paths Coverage: {coverage_report.critical_paths_covered:.1f}%",
                ""
            ])

            # Top covered modules
            sorted_modules = sorted(
                coverage_report.module_coverage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            report_lines.append("Top Covered Modules:")
            for module, coverage in sorted_modules:
                status = "✅" if coverage >= 90 else "⚠️" if coverage >= 70 else "❌"
                report_lines.append(f"  {status} {module}: {coverage:.1f}%")

            report_lines.append("")

            # Modules needing attention
            low_coverage = [(m, c) for m, c in coverage_report.module_coverage.items() if c < 70]
            if low_coverage:
                report_lines.extend([
                    "⚠️  MODULES NEEDING ATTENTION (< 70% coverage):",
                    "-" * 40
                ])
                for module, coverage in sorted(low_coverage, key=lambda x: x[1]):
                    missing_count = len(coverage_report.missing_lines.get(module, []))
                    report_lines.append(f"  ❌ {module}: {coverage:.1f}% ({missing_count} missing lines)")
                report_lines.append("")

        # Performance insights
        fastest_suite = min(self.results, key=lambda x: x.execution_time) if self.results else None
        slowest_suite = max(self.results, key=lambda x: x.execution_time) if self.results else None

        if fastest_suite and slowest_suite:
            report_lines.extend([
                "⚡ PERFORMANCE INSIGHTS:",
                "-" * 40,
                f"Fastest Suite: {fastest_suite.suite_name} ({fastest_suite.execution_time:.2f}s)",
                f"Slowest Suite: {slowest_suite.suite_name} ({slowest_suite.execution_time:.2f}s)",
                f"Average Suite Time: {total_time / len(self.results):.2f}s",
                ""
            ])

        # Quality assessment
        report_lines.extend([
            "🏆 QUALITY ASSESSMENT:",
            "-" * 40
        ])

        # Calculate quality score
        quality_factors = []

        # Test success rate (40% weight)
        quality_factors.append(("Test Success Rate", overall_success_rate * 0.4))

        # Coverage (30% weight)
        if coverage_report:
            quality_factors.append(("Code Coverage", coverage_report.total_coverage * 0.3))

        # Critical paths coverage (30% weight)
        if coverage_report:
            quality_factors.append(("Critical Paths", coverage_report.critical_paths_covered * 0.3))

        overall_quality = sum(factor[1] for factor in quality_factors)

        for factor_name, factor_score in quality_factors:
            report_lines.append(f"  {factor_name}: {factor_score:.1f}/100")

        report_lines.extend([
            f"  Overall Quality Score: {overall_quality:.1f}/100",
            ""
        ])

        # Recommendations
        report_lines.extend([
            "🚀 RECOMMENDATIONS:",
            "-" * 40
        ])

        if overall_success_rate < 95:
            report_lines.append("  • Investigate and fix failing tests")

        if coverage_report and coverage_report.total_coverage < 90:
            report_lines.append("  • Increase test coverage to reach 90% target")

        if coverage_report and coverage_report.critical_paths_covered < 95:
            report_lines.append("  • Focus on testing critical paths in core modules")

        if total_time > 60:
            report_lines.append("  • Consider optimizing slow test suites for faster feedback")

        if not coverage_report:
            report_lines.append("  • Install pytest and coverage tools for detailed analysis")

        report_lines.extend([
            "",
            "📝 REPORT COMPLETE",
            "=" * 80
        ])

        return "\n".join(report_lines)

    def run_comprehensive_test_suite(self) -> str:
        """Run all test suites and generate comprehensive report."""
        print("LOCALINSIGHTENGINE - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print("Starting comprehensive test execution...")

        start_time = time.perf_counter()

        # Run all test suites
        for suite_name, test_file in self.test_suites:
            result = self.run_single_test_suite(suite_name, test_file)
            self.results.append(result)

        # Run coverage analysis
        coverage_report = self.run_coverage_analysis()

        end_time = time.perf_counter()
        total_execution_time = end_time - start_time

        print(f"\n🏁 All test suites completed in {total_execution_time:.2f}s")

        # Generate and save report
        report = self.generate_comprehensive_report(coverage_report)

        # Save report to file
        report_path = self.project_root / "comprehensive_test_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Comprehensive report saved to: {report_path}")

        return report

    def save_results_json(self) -> Path:
        """Save test results in JSON format for CI/CD integration."""
        results_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "project": "LocalInsightEngine",
            "version": "0.1.1",
            "summary": {
                "total_suites": len(self.results),
                "total_tests": sum(r.tests_run for r in self.results),
                "total_failures": sum(r.failures for r in self.results),
                "total_errors": sum(r.errors for r in self.results),
                "total_skipped": sum(r.skipped for r in self.results),
                "total_time": sum(r.execution_time for r in self.results),
                "overall_success_rate": ((sum(r.tests_run for r in self.results) -
                                        sum(r.failures for r in self.results) -
                                        sum(r.errors for r in self.results)) /
                                       sum(r.tests_run for r in self.results) * 100) if sum(r.tests_run for r in self.results) > 0 else 0
            },
            "suites": [
                {
                    "name": r.suite_name,
                    "tests_run": r.tests_run,
                    "failures": r.failures,
                    "errors": r.errors,
                    "skipped": r.skipped,
                    "execution_time": r.execution_time,
                    "success_rate": r.success_rate
                }
                for r in self.results
            ]
        }

        json_path = self.project_root / "test_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2)

        return json_path


def main():
    """Main entry point for comprehensive test execution."""
    runner = ComprehensiveTestRunner()

    try:
        # Run comprehensive test suite
        report = runner.run_comprehensive_test_suite()

        # Save JSON results
        json_path = runner.save_results_json()
        print(f"📊 Test results saved to: {json_path}")

        # Print report
        print("\n" + report)

        # Return exit code based on test results
        total_failures = sum(r.failures for r in runner.results)
        total_errors = sum(r.errors for r in runner.results)

        if total_failures > 0 or total_errors > 0:
            print(f"\n❌ Tests failed - {total_failures} failures, {total_errors} errors")
            return 1
        else:
            print(f"\n✅ All tests passed successfully!")
            return 0

    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)