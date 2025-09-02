"""
Test script for PDF processing functionality.
"""

import sys
import random
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.text_processor import TextProcessor
from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient
from local_insight_engine.config.settings import Settings

def test_pdf_processing():
    """Test the PDF processing pipeline."""
    
    # Path to test PDF
    pdf_path = Path(r"C:\Users\diede\source\ClaudeProjekte\LocalInsightEngine\G-OMX-Readbook - zarko maroli Copy.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Test PDF not found: {pdf_path}")
        return
    
    print(f"[PDF] Testing PDF processing with: {pdf_path.name}")
    print("=" * 60)
    
    try:
        # Initialize components
        print("[INIT] Initializing components...")
        settings = Settings()
        loader = DocumentLoader()
        processor = TextProcessor(chunk_size=500, chunk_overlap=100)  # Smaller chunks for testing
        claude_client = ClaudeClient(settings)
        
        # Step 1: Load document (Layer 1)
        print("[LOAD] Loading document...")
        document = loader.load(pdf_path)
        
        print(f"SUCCESS: Document loaded successfully!")
        print(f"   - File format: {document.metadata.file_format}")
        print(f"   - File size: {document.metadata.file_size} bytes")
        print(f"   - Page count: {document.metadata.page_count}")
        print(f"   - Word count: {document.metadata.word_count}")
        print(f"   - Text length: {len(document.text_content)} characters")
        print(f"   - Paragraphs: {len(document.paragraph_mapping)}")
        print()
        
        # Show random sample of text
        sample_size = 350  # Slightly larger sample
        max_start = max(0, len(document.text_content) - sample_size)
        start_pos = random.randint(0, max_start)
        sample_text = document.text_content[start_pos:start_pos + sample_size]
        
        print(f"[SAMPLE] Random text sample ({sample_size} chars, starting at position {start_pos}):")
        print("-" * 40)
        print(sample_text + "...")
        print()
        
        # Step 2: Process text (Layer 2)
        print("[PROCESS] Processing text (neutralizing content)...")
        processed_text = processor.process(document)
        
        print(f"SUCCESS: Text processed successfully!")
        print(f"   - Total chunks: {processed_text.total_chunks}")
        print(f"   - Total entities: {processed_text.total_entities}")
        print(f"   - Processing time: {processed_text.processing_time_seconds:.2f} seconds")
        print(f"   - Key themes: {len(processed_text.key_themes)}")
        print()
        
        # Show some results
        if processed_text.key_themes:
            print("[THEMES] Extracted themes:")
            for theme in processed_text.key_themes[:5]:
                print(f"   - {theme}")
            print()
        
        if processed_text.all_entities:
            # Sample random entities instead of always the first 10
            sample_count = min(12, len(processed_text.all_entities))  # Show up to 12
            sampled_entities = random.sample(processed_text.all_entities, sample_count)
            
            print(f"[ENTITIES] Extracted entities (showing random {sample_count} of {len(processed_text.all_entities)}):")
            entity_types = {}
            for entity in sampled_entities:
                if entity.label not in entity_types:
                    entity_types[entity.label] = []
                entity_types[entity.label].append(entity.text)
            
            for entity_type, entities in entity_types.items():
                # Clean entities for Windows console display
                clean_entities = []
                for entity in entities:
                    try:
                        # Try to encode, if it fails, replace problem characters
                        entity.encode('cp1252')
                        clean_entities.append(entity)
                    except UnicodeEncodeError:
                        clean_entity = entity.encode('ascii', 'replace').decode('ascii')
                        clean_entities.append(clean_entity)
                print(f"   {entity_type}: {', '.join(clean_entities)}")
            print()
        
        if processed_text.chunks:
            print("[CONTENT] Sample neutralized content from first chunk:")
            print("-" * 40)
            first_chunk = processed_text.chunks[0]
            print(first_chunk.neutralized_content)
            print()
            
            if first_chunk.key_statements:
                print("[STATEMENTS] Key statements from first chunk:")
                for i, statement in enumerate(first_chunk.key_statements[:3], 1):
                    print(f"   {i}. {statement}")
                print()
        
        # Step 3: Claude Analysis (Layer 3)
        print("[ANALYSIS] Running Claude analysis...")
        analysis = claude_client.analyze(processed_text)
        
        print(f"SUCCESS: Claude analysis completed!")
        print(f"   - Status: {analysis.get('status', 'unknown')}")
        print(f"   - Model: {analysis.get('model', 'unknown')}")
        print(f"   - Confidence: {analysis.get('confidence_score', 0):.2f}")
        print(f"   - Insights: {len(analysis.get('insights', []))}")
        print(f"   - Questions: {len(analysis.get('questions', []))}")
        print()
        
        # Show analysis results
        if analysis.get('executive_summary'):
            print("[SUMMARY] Executive Summary:")
            print("-" * 40)
            print(analysis['executive_summary'][:300] + "..." if len(analysis['executive_summary']) > 300 else analysis['executive_summary'])
            print()
        
        if analysis.get('insights'):
            print(f"[INSIGHTS] Key Insights (showing first 2 of {len(analysis['insights'])}):")
            for i, insight in enumerate(analysis['insights'][:2], 1):
                print(f"   {i}. {insight.get('title', 'Unnamed Insight')}")
                if insight.get('content'):
                    content = insight['content'][:150] + "..." if len(insight['content']) > 150 else insight['content']
                    print(f"      {content}")
                print(f"      Confidence: {insight.get('confidence', 0):.2f}")
                print()
        
        print("SUCCESS: Complete pipeline test completed!")
        print("INFO: PDF -> Processing -> Claude analysis pipeline working correctly.")
        
    except Exception as e:
        print(f"ERROR: Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_processing()