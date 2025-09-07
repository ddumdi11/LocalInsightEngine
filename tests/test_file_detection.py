"""
Test file type detection and validation.
LocalInsightEngine v0.1.0 - File type validation test
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader


def test_file_type_detection():
    """Test file type detection for all available test files."""
    # Load from project root for consistent paths
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        loader = DocumentLoader()
    finally:
        os.chdir(original_cwd)
    
    print("FILE TYPE DETECTION TEST")
    print("=" * 40)
    
    # Test files to check
    test_files = [
        Path(__file__).parent.parent / "german_sample.txt",
        Path(__file__).parent.parent / "german_sample.pdf",
        Path(__file__).parent.parent / "english_sample.txt",
        Path(__file__).parent.parent / "english_sample.pdf"
    ]
    
    for file_path in test_files:
        if file_path.exists():
            print(f"\n[CHECK] {file_path.name}")
            file_info = loader.get_file_type_info(file_path)
            
            print(f"  Extension: .{file_info['extension']}")
            print(f"  Detected:  {file_info['detected_type']}")
            print(f"  Match:     {'YES' if file_info['matches'] else 'NO'}")
            print(f"  Supported: {'YES' if file_info['supported'] else 'NO'}")
            
            if not file_info['matches']:
                print(f"  WARNING: File type mismatch!")
            
        else:
            print(f"\n[SKIP] {file_path.name} - file not found")
    
    print("\n" + "=" * 40)
    print("File type detection test completed!")


def test_file_content_validation():
    """Test that files can actually be loaded with detected types."""
    # Load from project root for consistent paths
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        loader = DocumentLoader()
    finally:
        os.chdir(original_cwd)
    
    print("\nFILE CONTENT VALIDATION TEST")
    print("=" * 40)
    
    test_files = [
        Path(__file__).parent.parent / "german_sample.txt",
        Path(__file__).parent.parent / "english_sample.txt"
    ]
    
    for file_path in test_files:
        if file_path.exists():
            print(f"\n[VALIDATE] {file_path.name}")
            
            try:
                # Get file type info
                file_info = loader.get_file_type_info(file_path)
                print(f"  Detected as: {file_info['detected_type']}")
                
                # Try to load with detected type
                document = loader.load(file_path)
                print(f"  SUCCESS: Loaded {len(document.text_content)} characters")
                print(f"  Word count: {document.metadata.word_count}")
                print(f"  Format in metadata: {document.metadata.file_format}")
                
                # Quick content check (first 100 chars)
                preview = document.text_content[:100].replace('\n', ' ').strip()
                print(f"  Preview: {preview}...")
                
            except Exception as e:
                print(f"  ERROR: Failed to load - {e}")
        else:
            print(f"\n[SKIP] {file_path.name} - file not found")


def test_hypothetical_mismatch():
    """
    Demonstrate how the system would handle mismatched file extensions.
    (This is a conceptual test since we don't have actual mismatched files)
    """
    # Load from project root for consistent paths
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        loader = DocumentLoader()
    finally:
        os.chdir(original_cwd)
    
    print("\nHYPOTHETICAL MISMATCH TEST")
    print("=" * 35)
    print("This test shows how file type validation would work")
    print("if we had files with wrong extensions (e.g., PDF saved as .txt)")
    print()
    
    # Show current detection for existing files
    test_files = [
        Path(__file__).parent.parent / "german_sample.txt",
        Path(__file__).parent.parent / "german_sample.pdf"
    ]
    
    for file_path in test_files:
        if file_path.exists():
            file_info = loader.get_file_type_info(file_path)
            print(f"{file_path.name}:")
            print(f"  Expected: {file_info['extension']} | Detected: {file_info['detected_type']}")
            
            if file_info['matches']:
                print("  ✓ File extension matches content")
            else:
                print("  ⚠ MISMATCH: File content differs from extension!")
                print(f"    The system would use '{file_info['detected_type']}' parser instead")
            print()


if __name__ == "__main__":
    test_file_type_detection()
    test_file_content_validation()
    test_hypothetical_mismatch()