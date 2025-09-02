"""
Main entry point for LocalInsightEngine application.
"""

import logging
from pathlib import Path
from typing import Optional

from .config.settings import Settings
from .services.data_layer.document_loader import DocumentLoader
from .services.processing_hub.text_processor import TextProcessor
from .services.analysis_engine.claude_client import ClaudeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class LocalInsightEngine:
    """Main application class for LocalInsightEngine."""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.document_loader = DocumentLoader()
        self.text_processor = TextProcessor()
        self.llm_client = ClaudeClient(self.settings)
    
    def analyze_document(self, document_path: Path) -> dict:
        """
        Analyze a document through the 3-layer architecture.
        
        Args:
            document_path: Path to the document to analyze
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Starting analysis of document: {document_path}")
        
        # Layer 1: Load document
        document = self.document_loader.load(document_path)
        
        # Layer 2: Process and neutralize content
        processed_data = self.text_processor.process(document)
        
        # Layer 3: Analyze with LLM
        analysis = self.llm_client.analyze(processed_data)
        
        logger.info("Analysis completed successfully")
        return analysis


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python -m local_insight_engine.main <document_path>")
        sys.exit(1)
    
    document_path = Path(sys.argv[1])
    
    if not document_path.exists():
        print(f"Error: Document not found: {document_path}")
        sys.exit(1)
    
    engine = LocalInsightEngine()
    try:
        results = engine.analyze_document(document_path)
        print("Analysis Results:")
        print(results)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()