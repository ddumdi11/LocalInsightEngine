"""
Statistics Collector for comprehensive entity extraction analysis.
Tracks multi-stage entity processing with full transparency.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...models.analysis_statistics import (
    EntityDetail, EntityExtractionStage, EntityMergeAnalysis,
    ComplianceReport, ProcessingPerformance, DocumentAnalysisStatistics
)
from ...models.text_data import EntityData


class StatisticsCollector:
    """Collects comprehensive statistics during document processing."""

    def __init__(self):
        self.extraction_stages: List[EntityExtractionStage] = []
        self.performance_data: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}

        # Document metadata
        self.document_path: str = ""
        self.document_size: int = 0
        self.document_format: str = ""

        # Processing configuration
        self.factual_mode: bool = False
        self.bypass_anonymization: bool = False

        # Content statistics
        self.total_text_length: int = 0
        self.chunks_created: int = 0
        self.chunk_sizes: List[int] = []

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing and record duration."""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.performance_data[operation] = duration
            del self.start_times[operation]
            return duration
        return 0.0

    def set_document_info(self, path: str, size: int, format: str, text_length: int) -> None:
        """Record document metadata."""
        self.document_path = path
        self.document_size = size
        self.document_format = format
        self.total_text_length = text_length

    def set_processing_config(self, factual_mode: bool, bypass_anonymization: bool) -> None:
        """Record processing configuration."""
        self.factual_mode = factual_mode
        self.bypass_anonymization = bypass_anonymization

    def record_chunk_statistics(self, chunk_count: int, chunk_sizes: List[int]) -> None:
        """Record chunk creation statistics."""
        self.chunks_created = chunk_count
        self.chunk_sizes = chunk_sizes

    def record_entity_extraction_stage(
        self,
        stage_name: str,
        process_name: str,
        entities: List[EntityData],
        processing_time: float,
        anonymization_applied: bool = False
    ) -> None:
        """Record a complete entity extraction stage."""

        # Convert EntityData to EntityDetail
        entity_details = []
        confidences = []

        for entity in entities:
            detail = EntityDetail(
                text=entity.text,
                label=entity.label,
                confidence=entity.confidence,
                start_char=entity.start_char,
                end_char=entity.end_char,
                anonymized_text=getattr(entity, 'anonymized_text', None)
            )
            entity_details.append(detail)
            confidences.append(entity.confidence)

        # Calculate entity breakdown
        entity_breakdown = {}
        for entity in entities:
            label = entity.label
            entity_breakdown[label] = entity_breakdown.get(label, 0) + 1

        # Calculate confidence range
        conf_range = (min(confidences), max(confidences)) if confidences else (0.0, 0.0)

        # Count anonymization stats
        entities_anonymized = 0
        entities_preserved = 0

        if anonymization_applied:
            for entity in entities:
                if hasattr(entity, 'anonymized_text') and entity.anonymized_text != entity.text:
                    entities_anonymized += 1
                else:
                    entities_preserved += 1
        else:
            entities_preserved = len(entities)

        stage = EntityExtractionStage(
            stage_name=stage_name,
            process_name=process_name,
            total_entities=len(entities),
            entity_breakdown=entity_breakdown,
            processing_time_seconds=processing_time,
            confidence_range=conf_range,
            entities=entity_details,
            anonymization_applied=anonymization_applied,
            entities_anonymized=entities_anonymized,
            entities_preserved=entities_preserved
        )

        self.extraction_stages.append(stage)

    def _analyze_entity_overlaps(self, all_entities: List[EntityDetail]) -> EntityMergeAnalysis:
        """Analyze overlaps between different extraction stages."""

        # Group entities by text for overlap detection
        entity_groups = {}
        for entity in all_entities:
            key = entity.text.lower().strip()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)

        # Find duplicates
        duplicates_found = 0
        duplicate_examples = {}

        for key, group in entity_groups.items():
            if len(group) > 1:
                duplicates_found += len(group) - 1

                # Record example duplicates by label
                for entity in group:
                    if entity.label not in duplicate_examples:
                        duplicate_examples[entity.label] = []
                    if entity.text not in duplicate_examples[entity.label]:
                        duplicate_examples[entity.label].append(entity.text)

        # Calculate final breakdown after deduplication
        unique_entities = {}
        for key, group in entity_groups.items():
            # Take the entity with highest confidence
            best_entity = max(group, key=lambda e: e.confidence)
            label = best_entity.label
            unique_entities[label] = unique_entities.get(label, 0) + 1

        # Calculate merge quality (higher is better)
        total_before = len(all_entities)
        total_after = len(entity_groups)
        merge_quality = 1.0 - (duplicates_found / total_before) if total_before > 0 else 1.0

        stage_names = [stage.stage_name for stage in self.extraction_stages]

        return EntityMergeAnalysis(
            stages_processed=stage_names,
            total_entities_before_merge=total_before,
            duplicates_found=duplicates_found,
            duplicate_examples=duplicate_examples,
            total_entities_after_merge=total_after,
            final_entity_breakdown=unique_entities,
            merge_quality_score=merge_quality
        )

    def _generate_compliance_report(self, merge_analysis: EntityMergeAnalysis) -> ComplianceReport:
        """Generate legal compliance report."""

        # Find post-anonymization stage
        post_anon_stage = next(
            (s for s in self.extraction_stages if s.stage_name == "post_anonymization"),
            None
        )

        warnings = []
        original_names_in_output = []
        transmission_safe = True

        if not self.factual_mode and post_anon_stage:
            # In standard mode, check for any non-anonymized entities
            for entity in post_anon_stage.entities:
                if not entity.anonymized_text or entity.anonymized_text == entity.text:
                    # Original name detected in output!
                    original_names_in_output.append(entity.text)
                    warnings.append(f"Original entity '{entity.text}' not properly anonymized")
                    transmission_safe = False

        if self.factual_mode:
            warnings.append("Factual mode active - original entities preserved for scientific accuracy")

        # Assess risk level
        if not transmission_safe:
            risk_assessment = "HIGH"
        elif len(warnings) > 0:
            risk_assessment = "MEDIUM"
        else:
            risk_assessment = "LOW"

        return ComplianceReport(
            factual_mode_active=self.factual_mode,
            anonymization_required=not self.factual_mode,
            entities_ready_for_transmission=merge_analysis.total_entities_after_merge,
            original_names_detected_in_output=original_names_in_output,
            compliance_warnings=warnings,
            transmission_safe=transmission_safe,
            risk_assessment=risk_assessment
        )

    def generate_final_statistics(self) -> DocumentAnalysisStatistics:
        """Generate comprehensive statistics report."""

        # Collect all entities from all stages
        all_entities = []
        for stage in self.extraction_stages:
            all_entities.extend(stage.entities)

        # Analyze merges and overlaps
        merge_analysis = self._analyze_entity_overlaps(all_entities)

        # Generate compliance report
        compliance_report = self._generate_compliance_report(merge_analysis)

        # Calculate performance metrics
        performance = ProcessingPerformance(
            document_loading_seconds=self.performance_data.get("document_loading", 0.0),
            text_processing_seconds=self.performance_data.get("text_processing", 0.0),
            entity_extraction_total_seconds=sum(
                stage.processing_time_seconds for stage in self.extraction_stages
            ),
            entity_merge_seconds=self.performance_data.get("entity_merge", 0.0),
            llm_analysis_seconds=self.performance_data.get("llm_analysis", 0.0),
            total_processing_seconds=self.performance_data.get("total_processing", 0.0)
        )

        # Calculate chunk statistics
        chunk_size_range = (min(self.chunk_sizes), max(self.chunk_sizes)) if self.chunk_sizes else (0, 0)
        average_chunk_size = sum(self.chunk_sizes) / len(self.chunk_sizes) if self.chunk_sizes else 0

        return DocumentAnalysisStatistics(
            document_path=self.document_path,
            document_name=self.document_path.split("/")[-1].split("\\")[-1],
            document_size_bytes=self.document_size,
            document_format=self.document_format,
            total_text_length=self.total_text_length,
            chunks_created=self.chunks_created,
            chunk_size_range=chunk_size_range,
            average_chunk_size=average_chunk_size,
            extraction_stages=self.extraction_stages,
            merge_analysis=merge_analysis,
            compliance_report=compliance_report,
            factual_mode_enabled=self.factual_mode,
            bypass_anonymization=self.bypass_anonymization,
            custom_patterns_active=True,  # We always have custom patterns now
            performance=performance,
            llm_analysis_success=True,  # Will be updated later
            llm_insights_count=0,       # Will be updated later
            llm_questions_count=0,      # Will be updated later
        )