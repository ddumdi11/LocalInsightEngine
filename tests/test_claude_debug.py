"""
Debug Claude API JSON parsing issues.
LocalInsightEngine v0.1.0 - Claude API debugging & validation
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient
from local_insight_engine.config.settings import Settings
from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.text_processor import TextProcessor

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


def test_claude_direct():
    """Test Claude API directly with minimal data."""
    # Load from project root
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        print("CLAUDE API DEBUG TEST")
        print("=" * 40)
        
        settings = Settings()
        claude_client = ClaudeClient(settings)
        
        if not claude_client.client:
            print("ERROR: Claude client not initialized (no API key?)")
            return
        
        print(f"API Key found: {bool(settings.llm_api_key)}")
        print(f"Model: {settings.llm_model}")
        print()
        
        # Create minimal test data
        print("[TEST] Creating minimal test data...")
        
        # Simple mock processed text
        class MockProcessedText:
            def __init__(self):
                self.total_chunks = 3
                self.total_entities = 10
                self.key_themes = ["test", "example", "debug"]
                self.chunks = [MockChunk()]
                self.all_entities = []
        
        class MockChunk:
            def __init__(self):
                self.key_statements = [
                    "This is a test statement about debugging.",
                    "The system processes text data efficiently.",
                    "Analysis results should be structured clearly."
                ]
        
        processed_text = MockProcessedText()
        
        print("[ANALYSIS] Running minimal Claude analysis...")
        print(f"Test data: {processed_text.total_chunks} chunks, {processed_text.total_entities} entities")
        print()
        
        # Run analysis
        analysis = claude_client.analyze(processed_text)
        
        print("[RESULT] Analysis result:")
        print(f"Status: {analysis.get('status', 'unknown')}")
        print(f"Model: {analysis.get('model', 'unknown')}")
        
        if analysis.get('status') == 'success':
            print("✓ SUCCESS: Real Claude analysis completed!")
            print(f"Summary: {analysis.get('executive_summary', 'N/A')}")
            print(f"Insights: {len(analysis.get('insights', []))}")
        else:
            print("✗ FAILED: Fell back to mock analysis")
            print("Check logs above for JSON parsing errors")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        os.chdir(original_cwd)


def test_claude_with_real_data():
    """Test Claude with real document processing."""
    # Load from project root
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        print("\n" + "=" * 50)
        print("CLAUDE WITH REAL DATA TEST")
        print("=" * 50)
        
        # Load a small sample of real text
        txt_file = project_root / "german_sample.txt"
        if not txt_file.exists():
            print("ERROR: german_sample.txt not found")
            return
        
        # Process a small portion
        loader = DocumentLoader()
        processor = TextProcessor(chunk_size=200, chunk_overlap=50)  # Small chunks
        claude_client = ClaudeClient(Settings())
        
        print("[LOAD] Loading small text sample...")
        document = loader.load(txt_file)
        
        # Take only first 1000 characters for quick test
        original_content = document.text_content
        document.text_content = original_content[:1000]
        
        print(f"Sample size: {len(document.text_content)} characters")
        
        print("[PROCESS] Processing sample...")
        processed_text = processor.process(document)
        
        print(f"Processed: {processed_text.total_chunks} chunks, {processed_text.total_entities} entities")
        
        print("[ANALYSIS] Running Claude analysis on real data...")
        analysis = claude_client.analyze(processed_text)
        
        print("[RESULT] Analysis result:")
        print(f"Status: {analysis.get('status', 'unknown')}")
        
        if analysis.get('status') == 'success':
            print("✓ SUCCESS: Real data analysis completed!")
            summary = analysis.get('executive_summary', '')
            print(f"Summary length: {len(summary)} chars")
            print(f"Summary: {summary[:200]}...")
        else:
            print("✗ FAILED: Fell back to mock analysis")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    test_claude_direct()
    test_claude_with_real_data()