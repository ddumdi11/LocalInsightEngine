"""
Analysis Statistics Models for Comprehensive Document Processing Reports
Provides full transparency with legal compliance for entity extraction processes.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EntityDetail(BaseModel):
    """Individual entity with full metadata."""
    text: str
    label: str
    confidence: float
    start_char: int
    end_char: int
    anonymized_text: Optional[str] = None  # What it becomes after anonymization


class EntityExtractionStage(BaseModel):
    """Statistics for a single stage of entity extraction."""

    stage_name: str  # "pre_anonymization", "post_anonymization", "statement_extractor"
    process_name: str  # "SpacyEntityExtractor", "SpacyStatementExtractor"

    # Core statistics
    total_entities: int
    entity_breakdown: Dict[str, int]  # {"NUTRIENT": 89, "NEUROCHEMICAL": 23}

    # Performance metrics
    processing_time_seconds: float
    confidence_range: Tuple[float, float]  # (min_conf, max_conf)

    # Full entity details for transparency and overlap analysis
    entities: List[EntityDetail]

    # Anonymization tracking
    anonymization_applied: bool
    entities_anonymized: int = 0
    entities_preserved: int = 0  # For factual mode


class EntityMergeAnalysis(BaseModel):
    """Analysis of entity merging across multiple extraction stages."""

    # Input statistics
    stages_processed: List[str]
    total_entities_before_merge: int

    # Overlap analysis
    duplicates_found: int
    duplicate_examples: Dict[str, List[str]]  # {"PERSON": ["Goethe", "Johann Goethe"]}

    # Final results
    total_entities_after_merge: int
    final_entity_breakdown: Dict[str, int]

    # Quality metrics
    merge_quality_score: float  # 0-1 score based on successful deduplication


class ComplianceReport(BaseModel):
    """Legal compliance analysis for entity handling."""

    factual_mode_active: bool
    anonymization_required: bool

    # Pre-transmission analysis
    entities_ready_for_transmission: int
    original_names_detected_in_output: List[str]  # Should be empty in standard mode!
    compliance_warnings: List[str]

    # Compliance status
    transmission_safe: bool
    risk_assessment: str  # "LOW", "MEDIUM", "HIGH"


class ProcessingPerformance(BaseModel):
    """Comprehensive performance metrics."""

    # Stage timings
    document_loading_seconds: float
    text_processing_seconds: float
    entity_extraction_total_seconds: float
    entity_merge_seconds: float
    llm_analysis_seconds: float
    total_processing_seconds: float

    # Resource usage
    peak_memory_mb: Optional[float] = None
    chunks_processed_per_second: Optional[float] = None
    entities_extracted_per_second: Optional[float] = None


class DocumentAnalysisStatistics(BaseModel):
    """Complete document analysis statistics with full transparency."""

    # Document metadata
    document_path: str
    document_name: str
    document_size_bytes: int
    document_format: str
    processing_timestamp: datetime = Field(default_factory=datetime.now)

    # Content analysis
    total_text_length: int
    chunks_created: int
    chunk_size_range: Tuple[int, int]  # (min_size, max_size)
    average_chunk_size: float

    # Multi-stage entity extraction
    extraction_stages: List[EntityExtractionStage]
    merge_analysis: EntityMergeAnalysis

    # Legal compliance
    compliance_report: ComplianceReport

    # Processing configuration
    factual_mode_enabled: bool
    bypass_anonymization: bool
    custom_patterns_active: bool

    # Performance metrics
    performance: ProcessingPerformance

    # LLM Analysis summary
    llm_analysis_success: bool
    llm_insights_count: int
    llm_questions_count: int
    llm_confidence_score: Optional[float] = None


class AnalysisReport(BaseModel):
    """Complete analysis report for UI display and export."""

    report_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.now)
    system_version: str = "0.1.1"

    # Main statistics
    statistics: DocumentAnalysisStatistics

    # Export configuration
    export_format: Optional[str] = None
    export_filename: Optional[str] = None

    def generate_export_filename(self, format_type: str) -> str:
        """Generate smart filename based on original document."""
        doc_path = Path(self.statistics.document_path)
        stem = doc_path.stem
        timestamp = self.generated_at.strftime("%Y%m%d_%H%M%S")
        return f"{stem}_analysis_report_{timestamp}.{format_type}"

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get key statistics for quick overview."""
        stats = self.statistics
        final_entities = stats.merge_analysis.total_entities_after_merge

        return {
            "document_name": stats.document_name,
            "processing_time": f"{stats.performance.total_processing_seconds:.2f}s",
            "chunks_created": stats.chunks_created,
            "entities_total": final_entities,
            "top_entity_types": dict(
                sorted(
                    stats.merge_analysis.final_entity_breakdown.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            ),
            "factual_mode": stats.factual_mode_enabled,
            "transmission_safe": stats.compliance_report.transmission_safe,
            "llm_success": stats.llm_analysis_success
        }

    def get_local_transparency_section(self) -> Dict[str, Any]:
        """Get data for local transparency display (full entity names)."""
        # Look for either pre_anonymization OR factual_mode_extraction stage
        pre_anon_stage = next(
            (s for s in self.statistics.extraction_stages if s.stage_name in ["pre_anonymization", "factual_mode_extraction"]),
            None
        )

        if not pre_anon_stage:
            return {"error": "No pre-anonymization data available"}

        # Group entities by type with original names
        entity_samples = {}
        for label, count in pre_anon_stage.entity_breakdown.items():
            sample_entities = [
                e.text for e in pre_anon_stage.entities
                if e.label == label
            ][:10]  # Show top 10 examples
            entity_samples[label] = {
                "count": count,
                "examples": sample_entities
            }

        return {
            "title": "🔍 ORIGINAL ENTITIES FOUND IN YOUR DOCUMENT",
            "total_entities": pre_anon_stage.total_entities,
            "entity_breakdown": entity_samples,
            "note": "These are the original entities extracted from your local document."
        }

    def get_transmission_preview_section(self) -> Dict[str, Any]:
        """Get data for transmission preview (anonymized entities)."""
        post_anon_stage = next(
            (s for s in self.statistics.extraction_stages if s.stage_name == "post_anonymization"),
            None
        )

        if not post_anon_stage:
            return {"error": "No post-anonymization data available"}

        # Show anonymized versions
        anonymized_samples = {}
        for label, count in post_anon_stage.entity_breakdown.items():
            sample_entities = [
                e.anonymized_text or e.text for e in post_anon_stage.entities
                if e.label == label
            ][:10]
            anonymized_samples[label] = {
                "count": count,
                "examples": sample_entities
            }

        compliance = self.statistics.compliance_report

        return {
            "title": "📡 WHAT WOULD BE SENT TO EXTERNAL APIS",
            "total_entities": post_anon_stage.total_entities,
            "entity_breakdown": anonymized_samples,
            "compliance_status": "✅ SAFE" if compliance.transmission_safe else "❌ RISK",
            "warnings": compliance.compliance_warnings,
            "note": "This shows the anonymized data that would be transmitted externally."
        }