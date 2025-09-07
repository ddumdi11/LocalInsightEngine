"""
Multi-format document processing tests.
Tests TXT files first (preferred), then PDFs as fallback.
Supports both German and English documents.
LocalInsightEngine v0.1.0 - Multi-format test (RECOMMENDED)
"""

import sys
import os
import random
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.text_processor import TextProcessor
from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient
from local_insight_engine.config.settings import Settings


class MultiFormatTestRunner:
    """Test runner for multi-format document processing with TXT priority."""
    
    def __init__(self):
        # Set up project root path
        self.project_root = Path(__file__).parent.parent
        
        # Load settings from project root (where .env is located)
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        try:
            self.settings = Settings()
            self.loader = DocumentLoader()
            self.processor = TextProcessor(chunk_size=400, chunk_overlap=80)
            self.claude_client = ClaudeClient(self.settings)
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
        
        # Define test files with TXT preference
        self.test_files = {
            'german': {
                'txt': Path(__file__).parent.parent / "german_sample.txt",
                'pdf': Path(__file__).parent.parent / "german_sample.pdf"
            },
            'english': {
                'txt': Path(__file__).parent.parent / "english_sample.txt",
                'pdf': Path(__file__).parent.parent / "english_sample.pdf"
            }
        }
    
    def find_available_files(self) -> Dict[str, Dict[str, bool]]:
        """Find which test files are available for each language."""
        available = {}
        for language, formats in self.test_files.items():
            available[language] = {}
            for format_type, path in formats.items():
                available[language][format_type] = path.exists()
                if not path.exists():
                    print(f"WARNING: {language} {format_type.upper()} not found at {path}")
        return available
    
    def get_preferred_file(self, language: str) -> Tuple[Path, str]:
        """Get the preferred file format for a language (TXT first, PDF fallback)."""
        formats = self.test_files[language]
        
        # Prefer TXT over PDF (higher quality, no extraction errors)
        if formats['txt'].exists():
            return formats['txt'], 'txt'
        elif formats['pdf'].exists():
            return formats['pdf'], 'pdf'
        else:
            raise FileNotFoundError(f"No files found for {language}")
    
    def extract_random_sample(self, text: str, sample_size: int = 300) -> dict:
        """Extract a random text sample from document."""
        if len(text) <= sample_size:
            return {
                'text': text,
                'start_pos': 0,
                'end_pos': len(text),
                'size': len(text)
            }
        
        max_start = len(text) - sample_size
        start_pos = random.randint(0, max_start)
        sample_text = text[start_pos:start_pos + sample_size]
        
        return {
            'text': sample_text,
            'start_pos': start_pos,
            'end_pos': start_pos + sample_size,
            'size': sample_size
        }
    
    def test_single_language_format(self, language: str, file_path: Path, file_format: str) -> dict:
        """Test processing for a single language and format."""
        print(f"[{language.upper()}] Testing {language} document processing...")
        print(f"Format: {file_format.upper()}")
        print(f"File: {file_path.name}")
        
        # Check actual file type vs expected
        file_info = self.loader.get_file_type_info(file_path)
        print(f"Extension: .{file_info['extension']} | Detected: {file_info['detected_type']} | Match: {file_info['matches']}")
        
        if file_format == 'txt':
            print("PRIORITY: Using high-quality TXT file!")
        else:
            print("FALLBACK: Using PDF file")
        print("=" * 50)
        
        try:
            # Load document
            print("[LOAD] Loading document...")
            document = self.loader.load(file_path)
            
            print(f"SUCCESS: Document loaded successfully!")
            print(f"  - Format: {file_format}")
            print(f"  - Pages: {document.metadata.page_count if hasattr(document.metadata, 'page_count') else 'N/A'}")
            print(f"  - Words: {document.metadata.word_count}")
            print(f"  - Characters: {len(document.text_content)}")
            
            # Extract random sample
            sample = self.extract_random_sample(document.text_content)
            print(f"\n[SAMPLE] Random text sample ({language}):")
            print("-" * 30)
            print(sample['text'][:200] + "..." if len(sample['text']) > 200 else sample['text'])
            
            # Process text
            print(f"\n[PROCESS] Processing {language} text...")
            processed_text = self.processor.process(document)
            
            print(f"SUCCESS: Processing completed!")
            print(f"  - Chunks: {processed_text.total_chunks}")
            print(f"  - Entities: {processed_text.total_entities}")
            print(f"  - Time: {processed_text.processing_time_seconds:.2f}s")
            
            # Show language-specific entities (sample)
            if processed_text.all_entities:
                sample_entities = random.sample(
                    processed_text.all_entities, 
                    min(8, len(processed_text.all_entities))
                )
                print(f"\n[ENTITIES] Sample entities ({language}):")
                entity_groups = {}
                for entity in sample_entities:
                    if entity.label not in entity_groups:
                        entity_groups[entity.label] = []
                    entity_groups[entity.label].append(entity.text)
                
                for label, entities in entity_groups.items():
                    print(f"  {label}: {', '.join(entities[:3])}")
            
            # Claude analysis
            print(f"\n[ANALYSIS] Running Claude analysis for {language}...")
            analysis = self.claude_client.analyze(processed_text)
            
            print(f"SUCCESS: Analysis completed!")
            print(f"  - Status: {analysis.get('status', 'unknown')}")
            print(f"  - Confidence: {analysis.get('confidence_score', 0):.2f}")
            print(f"  - Insights: {len(analysis.get('insights', []))}")
            
            # Show summary
            if analysis.get('executive_summary'):
                summary = analysis['executive_summary']
                print(f"\n[SUMMARY] {language.capitalize()} document summary:")
                print("-" * 30)
                print(summary[:250] + "..." if len(summary) > 250 else summary)
            
            return {
                'language': language,
                'format': file_format,
                'success': True,
                'document': document,
                'processed': processed_text,
                'analysis': analysis,
                'sample': sample
            }
            
        except Exception as e:
            print(f"ERROR processing {language} document: {e}")
            return {
                'language': language,
                'format': file_format,
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive multi-format test suite."""
        print("MULTI-FORMAT DOCUMENT PROCESSING TEST")
        print("(TXT preferred, PDF fallback)")
        print("=" * 60)
        
        available_files = self.find_available_files()
        
        # Test each available language with preferred format
        results = []
        languages_with_files = [lang for lang, formats in available_files.items() 
                              if any(formats.values())]
        
        if not languages_with_files:
            print("ERROR: No test files found!")
            return
        
        print(f"Available languages: {', '.join(languages_with_files)}")
        print()
        
        for language in languages_with_files:
            try:
                file_path, file_format = self.get_preferred_file(language)
                result = self.test_single_language_format(language, file_path, file_format)
                results.append(result)
                print()  # Space between language tests
            except FileNotFoundError as e:
                print(f"ERROR: {e}")
                continue
        
        # Final summary
        successful_tests = sum(1 for r in results if r['success'])
        print(f"\n" + "=" * 60)
        print(f"TEST SUMMARY: {successful_tests}/{len(results)} languages processed successfully")
        
        if successful_tests > 0:
            print("SUCCESS: Multi-format pipeline working correctly!")
            
            # Show format distribution
            txt_successful = sum(1 for r in results if r['success'] and r['format'] == 'txt')
            pdf_successful = sum(1 for r in results if r['success'] and r['format'] == 'pdf')
            print(f"Format distribution: {txt_successful} TXT (preferred), {pdf_successful} PDF (fallback)")
            
            if txt_successful > 0:
                print("EXCELLENT: High-quality TXT files are being used!")
        else:
            print("ERROR: All language tests failed!")
        
        return results


def test_txt_priority():
    """Test TXT priority over PDF."""
    runner = MultiFormatTestRunner()
    
    print("TXT PRIORITY TEST")
    print("=" * 30)
    
    for language in ['german', 'english']:
        print(f"\n{language.upper()}:")
        try:
            file_path, file_format = runner.get_preferred_file(language)
            print(f"  Preferred format: {file_format.upper()}")
            print(f"  File: {file_path.name}")
            if file_format == 'txt':
                print("  SUCCESS: TXT file is preferred!")
            else:
                print("  FALLBACK: Using PDF (TXT not available)")
        except FileNotFoundError:
            print(f"  ERROR: No files available for {language}")


if __name__ == "__main__":
    # Main comprehensive test (TXT preferred, PDF fallback)
    runner = MultiFormatTestRunner()
    
    # First show priority test
    test_txt_priority()
    print("\n" + "="*60 + "\n")
    
    # Then run full test
    runner.run_comprehensive_test()