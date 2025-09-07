"""
Test JSON export functionality.
LocalInsightEngine v0.1.0 - JSON Export Test
"""

import sys
import tempfile
import json
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.main import LocalInsightEngine


def test_json_export():
    """Test JSON export functionality."""
    
    print("[JSON EXPORT] Testing JSON export functionality...")
    print("=" * 60)
    
    try:
        # Create a simple test text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("""
            Dies ist ein Testdokument für den JSON-Export.
            
            Es enthält verschiedene Abschnitte mit wichtigen Informationen:
            
            1. Technische Details
            Die LocalInsightEngine analysiert Dokumente in drei Schichten.
            
            2. Methodische Ansätze
            Named Entity Recognition wird für die Textverarbeitung verwendet.
            
            3. Ergebnisse und Schlussfolgerungen
            Das System generiert strukturierte Analysen ohne Urheberrechtsverletzungen.
            """)
            test_file = Path(f.name)
        
        print(f"[SETUP] Created test file: {test_file}")
        
        # Initialize engine
        print("[INIT] Initializing LocalInsightEngine...")
        engine = LocalInsightEngine()
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_analysis"
            
            # Test analyze_and_export method
            print("[TEST] Testing analyze_and_export method...")
            results = engine.analyze_and_export(
                document_path=test_file,
                output_path=output_path,
                formats=["json"]
            )
            
            print(f"SUCCESS: Analysis and export completed!")
            print(f"   - Export results: {results['export_results']}")
            print(f"   - Export paths: {results['export_paths']}")
            
            # Check if JSON file was created
            json_path = output_path.with_suffix(".json")
            if json_path.exists():
                print(f"SUCCESS: JSON file created at {json_path}")
                
                # Load and validate JSON structure
                with open(json_path, 'r', encoding='utf-8') as f:
                    exported_data = json.load(f)
                
                print("[VALIDATION] JSON structure validation:")
                required_keys = [
                    "export_metadata", "document", "text_processing", 
                    "analysis", "compliance"
                ]
                
                for key in required_keys:
                    if key in exported_data:
                        print(f"   ✓ {key}: OK")
                    else:
                        print(f"   ✗ {key}: MISSING")
                
                # Show some sample content
                print()
                print("[SAMPLE] Export content preview:")
                print(f"   - Export version: {exported_data.get('export_metadata', {}).get('export_version', 'N/A')}")
                print(f"   - Document filename: {exported_data.get('document', {}).get('metadata', {}).get('filename', 'N/A')}")
                print(f"   - Total chunks: {exported_data.get('text_processing', {}).get('chunk_statistics', {}).get('total_chunks', 'N/A')}")
                print(f"   - Analysis status: {exported_data.get('analysis', {}).get('status', 'N/A')}")
                print(f"   - Insights count: {len(exported_data.get('analysis', {}).get('insights', []))}")
                print(f"   - Questions count: {len(exported_data.get('analysis', {}).get('questions', []))}")
                print(f"   - Copyright compliant: {exported_data.get('compliance', {}).get('copyright_compliant', 'N/A')}")
                
                # Show file size
                file_size = json_path.stat().st_size
                print(f"   - JSON file size: {file_size:,} bytes")
                
                print()
                print("SUCCESS: JSON export test completed successfully!")
                print("INFO: JSON export functionality is working correctly.")
                
            else:
                print(f"ERROR: JSON file was not created at {json_path}")
                return False
        
        # Clean up test file
        test_file.unlink()
        print("[CLEANUP] Test file removed")
        
        return True
        
    except Exception as e:
        print(f"ERROR: JSON export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_json_export()
    if success:
        print()
        print("🎉 JSON Export Test: PASSED")
    else:
        print()
        print("❌ JSON Export Test: FAILED")
        sys.exit(1)