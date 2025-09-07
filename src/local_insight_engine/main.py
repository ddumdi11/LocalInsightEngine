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
from .services.export.export_manager import ExportManager

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
        self.export_manager = ExportManager()
    
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
    
    def analyze_and_export(
        self, 
        document_path: Path, 
        output_path: Optional[Path] = None,
        formats: Optional[list] = None
    ) -> dict:
        """
        Analyze a document and export results in specified formats.
        
        Args:
            document_path: Path to the document to analyze
            output_path: Path for export files (without extension)
            formats: List of export formats (default: ["json"])
            
        Returns:
            Dictionary with analysis results and export status
        """
        if formats is None:
            formats = ["json"]
            
        logger.info(f"Starting analysis and export of document: {document_path}")
        
        # Layer 1: Load document
        document = self.document_loader.load(document_path)
        
        # Layer 2: Process and neutralize content
        processed_data = self.text_processor.process(document)
        
        # Layer 3: Analyze with LLM
        analysis = self.llm_client.analyze(processed_data)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = self.export_manager.generate_output_filename(document)
        
        # Export results
        export_results = self.export_manager.export_analysis(
            analysis, processed_data, document, output_path, formats
        )
        
        logger.info("Analysis and export completed successfully")
        
        return {
            "analysis": analysis,
            "export_results": export_results,
            "export_paths": {
                fmt: output_path.with_suffix(f".{fmt}") 
                for fmt in formats if export_results.get(fmt, False)
            }
        }
    
    def export_existing_analysis(
        self,
        analysis_result: dict,
        processed_text: any,
        document: any,
        output_path: Path,
        formats: Optional[list] = None
    ) -> dict:
        """
        Export existing analysis results.
        
        Args:
            analysis_result: Previously generated analysis results
            processed_text: Processed text data
            document: Document metadata
            output_path: Path for export files
            formats: List of export formats
            
        Returns:
            Export results dictionary
        """
        if formats is None:
            formats = ["json"]
            
        return self.export_manager.export_analysis(
            analysis_result, processed_text, document, output_path, formats
        )


def main():
    """CLI entry point."""
    import sys
    from . import __version__
    
    # Handle version flag
    if len(sys.argv) == 2 and sys.argv[1] in ["--version", "-v"]:
        print(f"LocalInsightEngine v{__version__}")
        sys.exit(0)
    
    # Handle help flag
    if len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h"]:
        print("LocalInsightEngine - Copyright-compliant document analysis")
        print(f"Version: {__version__}")
        print()
        print("Usage:")
        print("  python -m local_insight_engine.main <document_path> [--export] [--format json]")
        print("  python -m local_insight_engine.main --version")
        print("  python -m local_insight_engine.main --help")
        print()
        print("Arguments:")
        print("  document_path    Path to PDF, TXT, EPUB, or DOCX file to analyze")
        print()
        print("Options:")
        print("  --export         Export analysis results to file")
        print("  --format FORMAT  Export format: json (default: json)")
        print("  --output PATH    Output path (without extension)")
        print("  --version, -v    Show version information")
        print("  --help, -h       Show this help message")
        print()
        print("Examples:")
        print("  python -m local_insight_engine.main document.pdf")
        print("  python -m local_insight_engine.main document.pdf --export")
        print("  python -m local_insight_engine.main document.pdf --export --format json --output /path/to/results")
        sys.exit(0)
    
    # Parse arguments
    args = sys.argv[1:]
    if not args:
        print("LocalInsightEngine - Copyright-compliant document analysis")
        print("Usage: python -m local_insight_engine.main <document_path> [options]")
        print("       python -m local_insight_engine.main --help")
        sys.exit(1)
    
    # Extract document path (first non-option argument)
    document_path = None
    export_enabled = False
    export_format = "json"
    output_path = None
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--export":
            export_enabled = True
        elif arg == "--format":
            if i + 1 < len(args):
                export_format = args[i + 1]
                i += 1
            else:
                print("Error: --format requires a value")
                sys.exit(1)
        elif arg == "--output":
            if i + 1 < len(args):
                output_path = Path(args[i + 1])
                i += 1
            else:
                print("Error: --output requires a path")
                sys.exit(1)
        elif not arg.startswith("--"):
            if document_path is None:
                document_path = Path(arg)
            else:
                print(f"Error: Multiple document paths provided: {document_path}, {arg}")
                sys.exit(1)
        else:
            print(f"Error: Unknown option: {arg}")
            sys.exit(1)
        
        i += 1
    
    if document_path is None:
        print("Error: No document path provided")
        sys.exit(1)
    
    if not document_path.exists():
        print(f"Error: Document not found: {document_path}")
        sys.exit(1)
    
    engine = LocalInsightEngine()
    try:
        if export_enabled:
            print(f"Analyzing document and exporting to {export_format} format...")
            results = engine.analyze_and_export(
                document_path, 
                output_path, 
                [export_format]
            )
            
            print("Analysis completed successfully!")
            print(f"Results exported to: {list(results['export_paths'].values())}")
            
            if results['export_results'][export_format]:
                print(f"Export successful: {results['export_paths'][export_format]}")
            else:
                print(f"Export failed for format: {export_format}")
        else:
            print("Analyzing document...")
            results = engine.analyze_document(document_path)
            print("Analysis Results:")
            print(results)
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()