#!/usr/bin/env python3
"""
Test Context Window Expansion
Tests the new configurable context window functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_insight_engine.main import LocalInsightEngine

def test_context_window():
    """Test the new context window expansion feature."""

    print("=== CONTEXT WINDOW EXPANSION TEST ===\n")

    # Initialize engine
    engine = LocalInsightEngine()

    # Check current config settings
    context_before = engine.config.get('Search', 'context_chunks_before', fallback='2')
    context_after = engine.config.get('Search', 'context_chunks_after', fallback='3')

    print(f"Context Window Configuration:")
    print(f"  Chunks before hit: {context_before}")
    print(f"  Chunks after hit:  {context_after}")
    print()

    # Test question
    test_question = "Welche Informationen zu Vitamin B3 finden sich im Dokument?"

    print(f"Test Question: {test_question}")
    print("\n" + "=" * 60)

    try:
        # This will use the new context window expansion
        answer = engine.answer_question(test_question)

        print("✅ CONTEXT WINDOW EXPANSION SUCCESSFUL")
        print("\nAnswer with expanded context:")
        print("-" * 40)
        print(answer)
        print("-" * 40)

        print(f"\nAnswer length: {len(answer)} characters")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_context_window()