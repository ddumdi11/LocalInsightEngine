"""
Processing configuration models for LocalInsightEngine.

This module defines the centralized configuration system that replaces
the scattered boolean parameter approach (factual_mode vs bypass_anonymization).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProcessingMode(Enum):
    """Primary processing mode for document analysis."""

    STANDARD = "standard"
    FACTUAL = "factual"
    # Future extensions:
    # LEGAL = "legal"
    # MEDICAL = "medical"


class AnonymizationLevel(Enum):
    """Level of anonymization to apply to content."""

    NONE = "none"                    # No anonymization (debug/internal only)
    SCIENTIFIC_ONLY = "scientific"  # Preserve scientific terms only
    FULL = "full"                   # Full anonymization (default)


class ComplianceMode(Enum):
    """Export compliance mode for different content types."""

    STRICT = "strict"       # Full copyright compliance (default)
    FACTUAL = "factual"     # Scientific/factual content compliance


@dataclass
class ProcessingConfig:
    """
    Centralized configuration for document processing modes.

    This replaces the scattered boolean parameters (factual_mode, bypass_anonymization)
    with a clean, extensible configuration object.

    Examples:
        # Standard mode (default)
        config = ProcessingConfig()

        # Factual mode
        config = ProcessingConfig.factual_mode()

        # Custom configuration
        config = ProcessingConfig(
            processing_mode=ProcessingMode.FACTUAL,
            preserve_scientific_terms=True,
            enable_semantic_triples=True
        )
    """

    # Primary processing mode
    processing_mode: ProcessingMode = ProcessingMode.STANDARD

    # Feature flags
    preserve_scientific_terms: bool = False
    enable_semantic_triples: bool = False
    enable_entity_equivalence: bool = True

    # Anonymization settings
    anonymization_level: AnonymizationLevel = AnonymizationLevel.FULL

    # Export settings
    export_compliance_mode: ComplianceMode = ComplianceMode.STRICT

    # Legacy compatibility flags (internal use)
    _legacy_factual_mode: Optional[bool] = None
    _legacy_bypass_anonymization: Optional[bool] = None

    def __post_init__(self):
        """Validate configuration consistency."""
        # Auto-enable semantic triples for factual mode
        if self.processing_mode == ProcessingMode.FACTUAL:
            if not self.enable_semantic_triples:
                # Auto-correct for consistency
                object.__setattr__(self, 'enable_semantic_triples', True)

    @classmethod
    def factual_mode(cls) -> 'ProcessingConfig':
        """
        Factory method for factual/scientific content processing.

        This mode:
        - Preserves scientific terms (Vitamin B3, Niacin, etc.)
        - Enables semantic triples extraction
        - Uses factual compliance mode for exports
        - Minimal anonymization (scientific terms only)

        Returns:
            ProcessingConfig configured for factual content analysis
        """
        return cls(
            processing_mode=ProcessingMode.FACTUAL,
            preserve_scientific_terms=True,
            enable_semantic_triples=True,
            enable_entity_equivalence=True,
            anonymization_level=AnonymizationLevel.SCIENTIFIC_ONLY,
            export_compliance_mode=ComplianceMode.FACTUAL,
            _legacy_factual_mode=True,
            _legacy_bypass_anonymization=True
        )

    @classmethod
    def standard_mode(cls) -> 'ProcessingConfig':
        """
        Factory method for standard literary content processing.

        This mode:
        - Full anonymization of content
        - Classic neutralization pipeline
        - Strict copyright compliance
        - Entity detection with anonymization

        Returns:
            ProcessingConfig configured for standard content analysis
        """
        return cls(
            processing_mode=ProcessingMode.STANDARD,
            preserve_scientific_terms=False,
            enable_semantic_triples=False,
            enable_entity_equivalence=True,
            anonymization_level=AnonymizationLevel.FULL,
            export_compliance_mode=ComplianceMode.STRICT,
            _legacy_factual_mode=False,
            _legacy_bypass_anonymization=False
        )

    @classmethod
    def from_legacy_params(cls, factual_mode: bool = False, bypass_anonymization: bool = None) -> 'ProcessingConfig':
        """
        Create ProcessingConfig from legacy boolean parameters.

        This method provides backward compatibility during the migration period.

        Args:
            factual_mode: Legacy factual_mode parameter
            bypass_anonymization: Legacy bypass_anonymization parameter (if different from factual_mode)

        Returns:
            ProcessingConfig equivalent to legacy parameters
        """
        # Handle parameter consistency
        if bypass_anonymization is None:
            bypass_anonymization = factual_mode

        if factual_mode or bypass_anonymization:
            config = cls.factual_mode()
        else:
            config = cls.standard_mode()

        # Store legacy values for debugging/compatibility
        config._legacy_factual_mode = factual_mode
        config._legacy_bypass_anonymization = bypass_anonymization

        return config

    # Legacy compatibility properties
    @property
    def is_factual_mode(self) -> bool:
        """Legacy property: equivalent to factual_mode parameter."""
        return self.processing_mode == ProcessingMode.FACTUAL

    @property
    def bypass_anonymization(self) -> bool:
        """Legacy property: equivalent to bypass_anonymization parameter."""
        return self.anonymization_level != AnonymizationLevel.FULL

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/logging."""
        return {
            "processing_mode": self.processing_mode.value,
            "preserve_scientific_terms": self.preserve_scientific_terms,
            "enable_semantic_triples": self.enable_semantic_triples,
            "enable_entity_equivalence": self.enable_entity_equivalence,
            "anonymization_level": self.anonymization_level.value,
            "export_compliance_mode": self.export_compliance_mode.value,
            # Legacy compatibility for logs
            "legacy_factual_mode": self.is_factual_mode,
            "legacy_bypass_anonymization": self.bypass_anonymization
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        mode_desc = {
            ProcessingMode.STANDARD: "Standard Mode (Full Anonymization)",
            ProcessingMode.FACTUAL: "Factual Mode (Scientific Terms Preserved)"
        }

        return f"ProcessingConfig({mode_desc.get(self.processing_mode, self.processing_mode.value)})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"ProcessingConfig(mode={self.processing_mode.value}, "
            f"scientific_terms={self.preserve_scientific_terms}, "
            f"semantic_triples={self.enable_semantic_triples}, "
            f"anonymization={self.anonymization_level.value})"
        )