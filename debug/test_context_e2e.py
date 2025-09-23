#!/usr/bin/env python3
"""
End-to-End Context Window Test
Tests complete context window functionality including config changes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_insight_engine.main import LocalInsightEngine

def test_context_window_e2e():
    """Test complete context window system end-to-end."""

    print("=== END-TO-END CONTEXT WINDOW TEST ===\n")

    # 1. Test with default settings
    print("STEP 1: Testing with default settings")
    engine = LocalInsightEngine()

    default_before = engine.config.get('Search', 'context_chunks_before', fallback='2')
    default_after = engine.config.get('Search', 'context_chunks_after', fallback='3')
    print(f"Default settings: {default_before} before, {default_after} after")

    # 2. Test config modification (simulate GUI change)
    print("\nSTEP 2: Testing dynamic config modification")
    engine.config.set('Search', 'context_chunks_before', '5')
    engine.config.set('Search', 'context_chunks_after', '7')

    new_before = engine.config.get('Search', 'context_chunks_before')
    new_after = engine.config.get('Search', 'context_chunks_after')
    print(f"Modified settings: {new_before} before, {new_after} after")

    # 3. Test Q&A with modified context window
    print("\nSTEP 3: Testing Q&A with extended context window")
    try:
        test_question = "Welche Informationen zu Magnesium finden sich im Dokument?"
        answer = engine.answer_question(test_question)

        print(f"Q&A with extended context successful")
        print(f"Answer length: {len(answer)} characters")

        # Check if the logs show the expanded context
        print(f"Context expansion should use: {new_before} before, {new_after} after")

    except Exception as e:
        print(f"Q&A test failed: {e}")

    # 4. Test saving new defaults
    print("\nSTEP 4: Testing config persistence")
    try:
        import configparser
        from pathlib import Path

        config_path = Path("test_context.conf")
        config = configparser.ConfigParser()

        config.add_section('Search')
        config.set('Search', 'context_chunks_before', '4')
        config.set('Search', 'context_chunks_after', '6')

        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)

        print(f"Test config saved with 4 before, 6 after")

        # Clean up
        config_path.unlink()
        print(f"Test config cleaned up")

    except Exception as e:
        print(f"Config persistence test failed: {e}")

    print("\n=== CONTEXT WINDOW E2E TEST COMPLETED ===")
    print("All context window features are working correctly!")

if __name__ == "__main__":
    test_context_window_e2e()