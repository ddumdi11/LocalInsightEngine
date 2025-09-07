"""
Export manager for coordinating different export formats.
LocalInsightEngine v0.1.0 - Export Management Service
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .json_exporter import JsonExporter
from ...models.text_data import ProcessedText
from ...models.document import Document

logger = logging.getLogger(__name__)


class ExportManager:
    """Manages exports of analysis results to various formats."""
    
    def __init__(self):
        """Initialize export manager with available exporters."""
        self.json_exporter = JsonExporter()
        self.supported_formats = ["json"]  # Will expand with CSV, PDF later
    
    def export_analysis(
        self,
        analysis_result: Dict[str, Any],
        processed_text: ProcessedText,
        document: Document,
        output_path: Path,
        formats: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Export analysis results to one or more formats.
        
        Args:
            analysis_result: Analysis results from Claude/mock
            processed_text: Processed text data from Layer 2
            document: Original document metadata from Layer 1
            output_path: Base path for exports (without extension)
            formats: List of formats to export (default: ["json"])
            
        Returns:
            Dict mapping format names to success status
        """
        if formats is None:
            formats = ["json"]
        
        results = {}
        
        logger.info(f"Starting export to formats: {formats}")
        
        for format_name in formats:
            if format_name not in self.supported_formats:
                logger.warning(f"Unsupported export format: {format_name}")
                results[format_name] = False
                continue
            
            try:
                success = self._export_single_format(
                    format_name, analysis_result, processed_text, document, output_path
                )
                results[format_name] = success
                
                if success:
                    logger.info(f"Successfully exported {format_name} format")
                else:
                    logger.error(f"Failed to export {format_name} format")
                    
            except Exception as e:
                logger.error(f"Error exporting {format_name}: {e}")
                results[format_name] = False
        
        return results
    
    def _export_single_format(
        self,
        format_name: str,
        analysis_result: Dict[str, Any],
        processed_text: ProcessedText,
        document: Document,
        base_output_path: Path
    ) -> bool:
        """Export to a single format."""
        
        if format_name == "json":
            output_path = base_output_path.with_suffix(".json")
            return self.json_exporter.export_analysis(
                analysis_result, processed_text, document, output_path
            )
        
        # Future formats will be added here
        # elif format_name == "csv":
        #     return self._export_csv(...)
        # elif format_name == "pdf":
        #     return self._export_pdf(...)
        
        return False
    
    def generate_output_filename(
        self,
        document: Document,
        base_dir: Optional[Path] = None,
        include_timestamp: bool = True
    ) -> Path:
        """
        Generate a suitable output filename based on document metadata.
        
        Args:
            document: Document metadata
            base_dir: Base directory for output (default: current directory)
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path for the output file (without extension)
        """
        if base_dir is None:
            base_dir = Path.cwd()
        
        # Clean filename from document
        if document.metadata.file_path:
            # Remove extension and clean filename
            clean_name = document.metadata.file_path.stem
            # Replace problematic characters
            clean_name = "".join(c for c in clean_name if c.isalnum() or c in "._- ")
            clean_name = clean_name.replace(" ", "_")
        else:
            clean_name = "analysis"
        
        # Add timestamp if requested
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_name}_analysis_{timestamp}"
        else:
            filename = f"{clean_name}_analysis"
        
        return base_dir / filename
    
    def get_export_summary(
        self,
        analysis_result: Dict[str, Any],
        processed_text: ProcessedText,
        document: Document
    ) -> Dict[str, Any]:
        """
        Generate a summary of what would be exported.
        Useful for showing users what will be included before export.
        """
        return {
            "document_info": {
                "filename": document.metadata.file_path.name if document.metadata.file_path else None,
                "format": document.metadata.file_format,
                "size": f"{document.metadata.file_size:,} bytes",
                "pages": document.metadata.page_count,
                "words": f"{document.metadata.word_count:,}" if document.metadata.word_count else "N/A"
            },
            "processing_results": {
                "chunks": processed_text.total_chunks,
                "entities": processed_text.total_entities,
                "themes": len(processed_text.key_themes),
                "processing_time": f"{processed_text.processing_time_seconds:.2f}s"
            },
            "analysis_results": {
                "status": analysis_result.get("status", "unknown"),
                "model": analysis_result.get("model", "unknown"),
                "insights": len(analysis_result.get("insights", [])),
                "questions": len(analysis_result.get("questions", [])),
                "confidence": analysis_result.get("confidence_score", 0.0),
                "completeness": analysis_result.get("completeness_score", 0.0)
            },
            "export_options": {
                "supported_formats": self.supported_formats,
                "copyright_compliant": True,
                "contains_original_text": False
            }
        }