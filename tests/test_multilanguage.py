"""
Multi-language document processing tests.
Tests both German and English PDFs with random sampling.
"""

import sys
import os
import random
from pathlib import Path
from typing import List, Optional

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.text_processor import TextProcessor
from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient
from local_insight_engine.config.settings import Settings


class MultiLanguageTestRunner:
    """Test runner for multi-language document processing."""
    
    def __init__(self):
        # Load settings from project root (where .env is located)
        project_root = Path(__file__).parent.parent
        original_cwd = os.getcwd()
        os.chdir(project_root)
        try:
            self.settings = Settings()
            self.loader = DocumentLoader()
            self.processor = TextProcessor(chunk_size=400, chunk_overlap=80)
            self.claude_client = ClaudeClient(self.settings)
        finally:
            os.chdir(original_cwd)
        
        # Define test PDFs (update paths as needed)
        self.test_files = {
            'german': Path(__file__).parent.parent / "german_sample.pdf",
            'english': Path(__file__).parent.parent / "english_sample.pdf"
        }
    
    def find_available_pdfs(self) -> List[str]:
        """Find which test PDFs are available."""
        available = []
        for lang, path in self.test_files.items():
            if path.exists():
                available.append(lang)
            else:
                print(f"WARNING: {lang} PDF not found at {path}")
        return available
    
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
    
    def test_single_language(self, language: str, pdf_path: Path) -> dict:
        """Test processing for a single language."""
        print(f"[{language.upper()}] Testing {language} document processing...")
        print(f"File: {pdf_path.name}")
        print("=" * 50)
        
        try:
            # Load document
            print("[LOAD] Loading document...")
            document = self.loader.load(pdf_path)
            
            print(f"SUCCESS: Document loaded successfully!")
            print(f"  - Pages: {document.metadata.page_count}")
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
            
            # Show language-specific entities
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
                'success': False,
                'error': str(e)
            }
    
    def test_dual_language_comparison(self, results: List[dict]):
        """Compare results from different languages."""
        if len(results) < 2:
            print("\nNot enough results for comparison.")
            return
        
        print("\n" + "=" * 60)
        print("MULTI-LANGUAGE COMPARISON")
        print("=" * 60)
        
        successful_results = [r for r in results if r['success']]
        
        if len(successful_results) >= 2:
            # Compare document characteristics
            print("[COMPARISON] Document Characteristics:")
            for result in successful_results:
                doc = result['document']
                processed = result['processed']
                lang = result['language']
                print(f"  {lang.capitalize()}:")
                print(f"    - Pages: {doc.metadata.page_count}")
                print(f"    - Words: {doc.metadata.word_count}")
                print(f"    - Chunks: {processed.total_chunks}")
                print(f"    - Entities: {processed.total_entities}")
                print(f"    - Processing Time: {processed.processing_time_seconds:.2f}s")
            
            # Compare entity types
            print(f"\n[COMPARISON] Entity Type Distribution:")
            for result in successful_results:
                entities = result['processed'].all_entities
                entity_counts = {}
                for entity in entities:
                    entity_counts[entity.label] = entity_counts.get(entity.label, 0) + 1
                
                print(f"  {result['language'].capitalize()}:")
                sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
                for entity_type, count in sorted_entities[:5]:
                    print(f"    - {entity_type}: {count}")
            
            # Compare analysis confidence
            print(f"\n[COMPARISON] Analysis Quality:")
            for result in successful_results:
                analysis = result['analysis']
                lang = result['language']
                confidence = analysis.get('confidence_score', 0)
                insights_count = len(analysis.get('insights', []))
                print(f"  {lang.capitalize()}: Confidence {confidence:.2f}, {insights_count} insights")
    
    def run_comprehensive_test(self):
        """Run comprehensive multi-language test suite."""
        print("MULTI-LANGUAGE DOCUMENT PROCESSING TEST")
        print("=" * 60)
        
        available_languages = self.find_available_pdfs()
        
        if not available_languages:
            print("ERROR: No test PDFs found!")
            return
        
        print(f"Available languages: {', '.join(available_languages)}")
        print()
        
        # Test each available language
        results = []
        for language in available_languages:
            pdf_path = self.test_files[language]
            result = self.test_single_language(language, pdf_path)
            results.append(result)
            print()  # Space between language tests
        
        # Run comparison if multiple languages available
        self.test_dual_language_comparison(results)
        
        # Final summary
        successful_tests = sum(1 for r in results if r['success'])
        print(f"\n" + "=" * 60)
        print(f"TEST SUMMARY: {successful_tests}/{len(results)} languages processed successfully")
        
        if successful_tests > 0:
            print("SUCCESS: Multi-language pipeline working correctly!")
        else:
            print("ERROR: All language tests failed!")
        
        return results


def test_german_only():
    """Test only German PDF processing."""
    runner = MultiLanguageTestRunner()
    pdf_path = runner.test_files['german']
    
    if not pdf_path.exists():
        print(f"ERROR: German PDF not found: {pdf_path}")
        return
    
    result = runner.test_single_language('german', pdf_path)
    return result


def test_english_only():
    """Test only English PDF processing."""
    runner = MultiLanguageTestRunner()
    pdf_path = runner.test_files['english']
    
    if not pdf_path.exists():
        print(f"ERROR: English PDF not found: {pdf_path}")
        print("Please add an English PDF as 'english_sample.pdf' to the project root.")
        return
    
    result = runner.test_single_language('english', pdf_path)
    return result


def test_random_samples():
    """Test random samples from available PDFs."""
    runner = MultiLanguageTestRunner()
    available = runner.find_available_pdfs()
    
    if not available:
        print("ERROR: No test PDFs available!")
        return
    
    print("RANDOM SAMPLE TESTING")
    print("=" * 40)
    
    # Test random samples from each available language
    for language in available:
        print(f"\n[RANDOM] Testing random sample from {language} PDF...")
        pdf_path = runner.test_files[language]
        
        try:
            # Load and extract random sample
            document = runner.loader.load(pdf_path)
            sample = runner.extract_random_sample(document.text_content, 500)
            
            print(f"Sample from position {sample['start_pos']} ({language}):")
            print("-" * 30)
            print(sample['text'])
            print("-" * 30)
            
        except Exception as e:
            print(f"ERROR sampling {language}: {e}")


if __name__ == "__main__":
    # You can run different test modes:
    
    # 1. Comprehensive test (all available languages)
    runner = MultiLanguageTestRunner()
    runner.run_comprehensive_test()
    
    # 2. Individual language tests (uncomment to use)
    # test_german_only()
    # test_english_only()
    
    # 3. Random sample testing (uncomment to use)
    # test_random_samples()