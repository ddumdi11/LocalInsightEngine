"""
JSON exporter for analysis results.
LocalInsightEngine v0.1.0 - JSON Export Service
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ...models.analysis import AnalysisResult, Insight, Question
from ...models.text_data import ProcessedText
from ...models.document import Document

logger = logging.getLogger(__name__)


class JsonExporter:
    """Exports analysis results to structured JSON format."""
    
    def __init__(self):
        """Initialize JSON exporter."""
        pass
    
    def export_analysis(
        self,
        analysis_result: Dict[str, Any],
        processed_text: ProcessedText,
        document: Document,
        output_path: Path
    ) -> bool:
        """
        Export complete analysis results to JSON.
        
        Args:
            analysis_result: Analysis results from Claude/mock
            processed_text: Processed text data from Layer 2
            document: Original document metadata from Layer 1
            output_path: Path where to save the JSON file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            logger.info(f"Exporting analysis to JSON: {output_path}")
            
            # Create comprehensive export structure
            export_data = self._build_export_structure(
                analysis_result, processed_text, document
            )
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            logger.info(f"JSON export completed successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return False
    
    def _build_export_structure(
        self,
        analysis_result: Dict[str, Any],
        processed_text: ProcessedText,
        document: Document
    ) -> Dict[str, Any]:
        """Build the comprehensive export data structure."""
        
        export_timestamp = datetime.now().isoformat()
        
        return {
            # Export metadata
            "export_metadata": {
                "export_timestamp": export_timestamp,
                "export_version": "1.0",
                "localinsightengine_version": "0.1.1",
                "format": "json"
            },
            
            # Original document information
            "document": {
                "metadata": {
                    "filename": document.metadata.file_path.name if document.metadata.file_path else None,
                    "file_path": str(document.metadata.file_path) if document.metadata.file_path else None,
                    "file_format": document.metadata.file_format,
                    "file_size": document.metadata.file_size,
                    "page_count": document.metadata.page_count,
                    "word_count": document.metadata.word_count,
                    "created_at": document.metadata.created_at.isoformat() if document.metadata.created_at else None,
                    "author": document.metadata.author,
                    "title": document.metadata.title,
                    "language": document.metadata.language
                },
                "processing_stats": {
                    "total_chunks": processed_text.total_chunks,
                    "total_entities": processed_text.total_entities,
                    "processing_time_seconds": processed_text.processing_time_seconds,
                    "key_themes_count": len(processed_text.key_themes)
                }
            },
            
            # Layer 2 processing results
            "text_processing": {
                "key_themes": processed_text.key_themes,
                "entity_summary": self._build_entity_summary(processed_text),
                "chunk_statistics": {
                    "total_chunks": processed_text.total_chunks,
                    "avg_chunk_size": self._calculate_avg_chunk_size(processed_text),
                    "chunks_with_statements": len([c for c in processed_text.chunks if c.key_statements])
                }
            },
            
            # Layer 3 analysis results
            "analysis": {
                "status": analysis_result.get("status", "unknown"),
                "model": analysis_result.get("model", "unknown"),
                "confidence_score": analysis_result.get("confidence_score", 0.0),
                "completeness_score": analysis_result.get("completeness_score", 0.0),
                
                # Main analysis content
                "executive_summary": analysis_result.get("executive_summary", ""),
                "insights": self._format_insights(analysis_result.get("insights", [])),
                "questions": self._format_questions(analysis_result.get("questions", [])),
                "themes": analysis_result.get("themes", []),
                "key_relationships": analysis_result.get("key_relationships", {}),
                "contradictions": analysis_result.get("contradictions", []),
                "knowledge_gaps": analysis_result.get("knowledge_gaps", []),
                "recommendations": analysis_result.get("recommendations", [])
            },
            
            # Privacy and compliance info
            "compliance": {
                "copyright_compliant": True,
                "contains_original_text": False,
                "neutralization_applied": True,
                "note": "This export contains only neutralized, processed content. No original copyrighted text is included."
            }
        }
    
    def _build_entity_summary(self, processed_text: ProcessedText) -> Dict[str, Any]:
        """Build summary of extracted entities by type."""
        entity_summary = {}
        
        for entity in processed_text.all_entities:
            if entity.label not in entity_summary:
                entity_summary[entity.label] = {
                    "count": 0,
                    "examples": []
                }
            
            entity_summary[entity.label]["count"] += 1
            
            # Add up to 5 examples per entity type
            if len(entity_summary[entity.label]["examples"]) < 5:
                entity_summary[entity.label]["examples"].append(entity.text)
        
        return entity_summary
    
    def _calculate_avg_chunk_size(self, processed_text: ProcessedText) -> float:
        """Calculate average chunk size in characters."""
        if not processed_text.chunks:
            return 0.0
        
        total_length = sum(len(chunk.neutralized_content) for chunk in processed_text.chunks)
        return total_length / len(processed_text.chunks)
    
    def _format_insights(self, insights: list) -> list:
        """Format insights for JSON export."""
        formatted_insights = []
        
        for insight in insights:
            if isinstance(insight, dict):
                formatted_insights.append({
                    "title": insight.get("title", ""),
                    "content": insight.get("content", ""),
                    "confidence": insight.get("confidence", 0.0),
                    "category": insight.get("category", "general")
                })
        
        return formatted_insights
    
    def _format_questions(self, questions: list) -> list:
        """Format questions for JSON export."""
        formatted_questions = []
        
        for question in questions:
            if isinstance(question, dict):
                formatted_questions.append({
                    "question": question.get("question", ""),
                    "context": question.get("context", ""),
                    "question_type": question.get("question_type", "general"),
                    "priority": question.get("priority", 3)
                })
        
        return formatted_questions
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and other objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")