#!/usr/bin/env python3
"""
Test Orchestrator - Runs existing tests in logical TDD order

This orchestrates existing test files rather than duplicating test code.
Ensures we run tests in the order they were developed for better debugging.
"""

import logging
import pytest
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


# Initialize logger
logger = logging.getLogger(__name__)


class TestOrchestrator:
    """Orchestrates existing tests in TDD development order."""

    # COMPLETED TESTS ONLY - Entity Equivalence + Content Flow + Semantic Triples
    TEST_EXECUTION_ORDER: List[Tuple[str, str]] = [
        # ALL Entity Equivalence Tests (8 tests - COMPLETED)
        (
            "test_entity_equivalence.py::TestEntityEquivalenceMapper::"
            "test_mapper_initialization",
            "Entity Mapper Init"
        ),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_basic_predefined_equivalences", "Basic Entity Resolution"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_case_insensitive_resolution_red_phase", "Case Insensitive Resolution"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_vitamin_b3_variants_comprehensive", "Vitamin B3 Variants"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_unknown_entities", "Unknown Entities"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_empty_and_invalid_inputs", "Empty/Invalid Inputs"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_dynamic_equivalence_discovery", "Dynamic Discovery"),
        ("test_entity_equivalence.py::TestEntityEquivalenceMapper::test_equivalence_report_generation", "Equivalence Reports"),

        # ALL Content Flow Tests (5 tests - COMPLETED)
        ("test_content_flow.py::TestContentFlow::test_sachbuch_modus_preserves_scientific_terms", "Sachbuch Mode"),
        ("test_content_flow.py::TestContentFlow::test_normal_modus_anonymizes_content", "Normal Mode Anonymization"),
        ("test_content_flow.py::TestContentFlow::test_content_flow_consistency", "Flow Consistency"),
        ("test_content_flow.py::TestContentFlow::test_empty_content_handling", "Empty Content Handling"),
        ("test_content_flow.py::TestContentFlow::test_chunk_properties", "Chunk Properties"),

        # ALL Semantic Triples Tests (9 tests - COMPLETED)
        ("test_semantic_triples.py::TestSemanticTriples::test_extractor_initialization", "Semantic Triples Init"),
        ("test_semantic_triples.py::TestSemanticTriples::test_triple_extraction_from_simple_sentences", "Simple Triple Extraction"),
        ("test_semantic_triples.py::TestSemanticTriples::test_vitamin_b3_triple_extraction", "Vitamin B3 Triples"),
        ("test_semantic_triples.py::TestSemanticTriples::test_vitamin_b3_fact_search", "Vitamin B3 Fact Search"),
        ("test_semantic_triples.py::TestSemanticTriples::test_llm_context_formatting", "LLM Context Formatting"),
        ("test_semantic_triples.py::TestSemanticTriples::test_edge_cases", "Semantic Edge Cases"),
        ("test_semantic_triples.py::TestSemanticTriples::test_ist_constructions_red_phase", "German Copula Constructions"),
        ("test_semantic_triples.py::TestSemanticTriples::test_complex_sentences_red_phase", "Complex German Sentences"),
        ("test_semantic_triples.py::TestSemanticTriples::test_negation_constructions_red_phase", "German Negation Constructions"),

        # END-TO-END WORKFLOW TESTS (E2E - Integration Tests)
        ("e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_complete_sachbuch_analysis_workflow", "E2E Sachbuch Analysis Workflow"),
        ("e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_qa_session_workflow", "E2E Q&A Session Workflow"),
        ("e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_analysis_report_generation_workflow", "E2E Analysis Report Workflow"),
        ("e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_persistence_workflow", "E2E Persistence Workflow"),
        ("e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_error_handling_workflow", "E2E Error Handling Workflow"),
    ]

    def test_run_completed_tests_in_order(self) -> None:
        """Run all COMPLETED tests in TDD development order."""
        failed_tests: List[Tuple[str, str, str, str]] = []
        failed_at_step: int = 0

        logger.info("\n%s", "=" * 60)
        logger.info("🧪 RUNNING COMPLETED TESTS IN TDD ORDER")
        logger.info("%s", "=" * 60)

        for i, (test_path, description) in enumerate(self.TEST_EXECUTION_ORDER, 1):
            failed_at_step = i
            logger.info("\n[%d/%d] %s", i, len(self.TEST_EXECUTION_ORDER), description)
            logger.info("Running: %s", test_path)

            try:
                # Run individual test
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=300)
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.error("Failed to run test %s: %s", test_path, str(e))
                failed_tests.append((test_path, description, "", str(e)))
                break

            if result.returncode == 0:
                logger.info("✅ PASSED: %s", description)
            else:
                logger.error("❌ FAILED: %s", description)
                logger.debug("STDOUT for failed test:\n%s", result.stdout)
                logger.debug("STDERR for failed test:\n%s", result.stderr)
                failed_tests.append((test_path, description, result.stdout, result.stderr))
                # Stop on first failure (like -x flag)
                break

        logger.info("\n%s", "=" * 60)
        if failed_tests:
            logger.error(
                "❌ COMPLETED TEST SUITE FAILED at step %d", failed_at_step
            )
            test_path, description, stdout, stderr = failed_tests[0]
            logger.error("Failed test: %s", description)
            logger.error("Path: %s", test_path)
            logger.error("\nSTDOUT:")
            logger.error("%s", stdout)
            if stderr:
                logger.error("\nSTDERR:")
                logger.error("%s", stderr)
            assert False, f"COMPLETED test suite failed at: {description}"
        else:
            logger.info(
                "✅ ALL %d COMPLETED TESTS PASSED!", len(self.TEST_EXECUTION_ORDER)
            )
        logger.info("%s", "=" * 60)


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    # Run orchestrator
    pytest.main([__file__, "-v", "-s"])