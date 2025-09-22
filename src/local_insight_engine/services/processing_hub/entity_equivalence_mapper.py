"""
Entity Equivalence Mapper - Resolves scientific naming variations to canonical forms.
Handles Niacin = Vitamin B3, chemical names, and terminological normalization.
"""

import logging
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import re

from ...models.text_data import EntityData

logger = logging.getLogger(__name__)


class EntityEquivalenceMapper:
    """
    Maps scientific entities to their canonical forms for consistent triple extraction.

    Handles:
    - Scientific names ↔ Common names (Niacin ↔ Vitamin B3)
    - Chemical nomenclature variations
    - Alternative spellings and abbreviations
    - Dynamic equivalence detection within documents
    """

    def __init__(self) -> None:
        # Predefined scientific equivalences
        self.predefined_equivalences = {
            # B-Vitamins
            "Vitamin_B3": {
                "primary_name": "Vitamin_B3",
                "scientific_names": ["Niacin", "Nicotinamid", "Nikotinamid", "Nicotinic acid"],
                "alternative_names": ["Vitamin B-3", "B3-Vitamin", "B3", "Vitamin B 3"],
                "chemical_names": ["Pyridine-3-carboxylic acid"]
            },
            "Vitamin_B1": {
                "primary_name": "Vitamin_B1",
                "scientific_names": ["Thiamin", "Thiamine"],
                "alternative_names": ["Vitamin B-1", "B1-Vitamin", "B1"],
                "chemical_names": []
            },
            "Vitamin_B2": {
                "primary_name": "Vitamin_B2",
                "scientific_names": ["Riboflavin"],
                "alternative_names": ["Vitamin B-2", "B2-Vitamin", "B2"],
                "chemical_names": []
            },
            "Vitamin_B6": {
                "primary_name": "Vitamin_B6",
                "scientific_names": ["Pyridoxin", "Pyridoxine"],
                "alternative_names": ["Vitamin B-6", "B6-Vitamin", "B6"],
                "chemical_names": []
            },
            "Vitamin_B12": {
                "primary_name": "Vitamin_B12",
                "scientific_names": ["Cobalamin", "Cyanocobalamin"],
                "alternative_names": ["Vitamin B-12", "B12-Vitamin", "B12"],
                "chemical_names": []
            },

            # Other vitamins
            "Vitamin_D": {
                "primary_name": "Vitamin_D",
                "scientific_names": ["Cholecalciferol", "Ergocalciferol"],
                "alternative_names": ["Vitamin D3", "Vitamin D2"],
                "chemical_names": []
            },

            # Minerals
            "Magnesium": {
                "primary_name": "Magnesium",
                "scientific_names": ["Mg"],
                "alternative_names": ["Magnesium"],
                "chemical_names": []
            },
            "Calcium": {
                "primary_name": "Calcium",
                "scientific_names": ["Ca"],
                "alternative_names": ["Kalzium"],
                "chemical_names": []
            }
        }

        # Dynamic equivalences discovered in current document
        self.dynamic_equivalences = {}

        # Reverse lookup: alternative name -> primary name
        self.name_to_primary = {}
        self._build_lookup_table()

    def _build_lookup_table(self) -> None:
        """Build reverse lookup table from all name variations to primary names."""
        self.name_to_primary = {}

        for primary_name, equivalence in self.predefined_equivalences.items():
            # Primary name maps to itself
            self.name_to_primary[primary_name.lower()] = primary_name

            # All alternative forms map to primary
            all_alternatives = (
                equivalence["scientific_names"] +
                equivalence["alternative_names"] +
                equivalence["chemical_names"]
            )

            for alt_name in all_alternatives:
                self.name_to_primary[alt_name.lower()] = primary_name

    def discover_document_equivalences(self, all_entities: List[EntityData]) -> None:
        """
        Discover entity equivalences within a document based on co-occurrence patterns.

        Strategy:
        1. Group entities by semantic similarity
        2. Find entities appearing in similar contexts
        3. Detect definitional patterns ("X, also known as Y")
        """
        logger.info(f"Analyzing {len(all_entities)} entities for equivalences")

        # Group entities by label type
        entities_by_label = defaultdict(list)
        for entity in all_entities:
            entities_by_label[entity.label].append(entity)

        # Look for definitional patterns in source sentences
        self._detect_definitional_patterns(all_entities)

        # Look for co-occurrence patterns
        self._detect_cooccurrence_patterns(entities_by_label)

        logger.info(f"Discovered {len(self.dynamic_equivalences)} dynamic equivalences")

    def _detect_definitional_patterns(self, entities: List[EntityData]) -> None:
        """
        Detect definitional patterns like:
        - "Vitamin B3 (Niacin)"
        - "Niacin, also known as Vitamin B3"
        - "Vitamin B3 oder Niacin"
        """
        definitional_patterns = [
            r'([^,\(]+)\s*\(([^)]+)\)',                    # "Vitamin B3 (Niacin)"
            r'([^,]+),\s*(?:also known as|auch bekannt als)\s*([^,\.]+)',  # "X, also known as Y"
            r'([^,]+)\s+(?:oder|or)\s+([^,\.]+)',         # "X oder Y"
            r'([^,]+),\s*(?:genannt|called)\s*([^,\.]+)'   # "X, genannt Y"
        ]

        for entity in entities:
            source_sentence = getattr(entity, 'source_sentence', None)
            if source_sentence:
                sentence = source_sentence

                for pattern in definitional_patterns:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        term1 = match.group(1).strip()
                        term2 = match.group(2).strip()

                        # Normalize both terms
                        norm1 = self._normalize_entity_name(term1)
                        norm2 = self._normalize_entity_name(term2)

                        if norm1 and norm2 and norm1 != norm2:
                            # Prefer the more "canonical" looking term as primary
                            primary, secondary = self._choose_primary_term(norm1, norm2)
                            self.dynamic_equivalences[secondary] = primary
                            logger.debug(f"Found equivalence: {secondary} = {primary}")

    def _detect_cooccurrence_patterns(self, entities_by_label: Dict[str, List[EntityData]]) -> None:
        """
        Detect entities that frequently co-occur in similar contexts.
        This is a simpler heuristic for now.
        """
        # For nutrients/chemicals, look for entities appearing in same paragraphs
        nutrient_entities = entities_by_label.get('NUTRIENT', [])

        for i, entity1 in enumerate(nutrient_entities):
            for entity2 in nutrient_entities[i+1:]:
                # Check if they appear in same paragraph/page
                if (entity1.source_paragraph_id == entity2.source_paragraph_id and
                    entity1.source_paragraph_id is not None):

                    # Simple heuristic: if they're both nutrients in same paragraph,
                    # they might be the same substance
                    name1 = self._normalize_entity_name(entity1.text)
                    name2 = self._normalize_entity_name(entity2.text)

                    if name1 and name2 and self._might_be_equivalent(name1, name2):
                        primary, secondary = self._choose_primary_term(name1, name2)
                        self.dynamic_equivalences[secondary] = primary
                        logger.debug(f"Co-occurrence equivalence: {secondary} = {primary}")

    def _might_be_equivalent(self, name1: str, name2: str) -> bool:
        """
        Heuristic to determine if two entity names might be equivalent.
        """
        # Check for obvious vitamin patterns
        if ('vitamin' in name1.lower() and 'b' in name1.lower() and
            any(alt in name2.lower() for alt in ['niacin', 'thiamin', 'riboflavin'])):
            return True

        # Check for similar length and character overlap
        if abs(len(name1) - len(name2)) < 3:
            overlap = len(set(name1.lower()) & set(name2.lower()))
            return overlap > min(len(name1), len(name2)) * 0.6

        return False

    def _choose_primary_term(self, term1: str, term2: str) -> Tuple[str, str]:
        """
        Choose which term should be the primary (canonical) form.
        Prefers structured scientific naming.
        """
        # Prefer "Vitamin_X" format
        if 'vitamin' in term1.lower() and 'vitamin' not in term2.lower():
            return term1, term2
        elif 'vitamin' in term2.lower() and 'vitamin' not in term1.lower():
            return term2, term1

        # Prefer longer, more descriptive names
        if len(term1) > len(term2):
            return term1, term2
        else:
            return term2, term1

    def _normalize_entity_name(self, entity_name: str) -> str:
        """
        Normalize entity name to canonical form.

        Canonical form: Title_Case_With_Underscores (e.g., "Vitamin_B3")

        Args:
            entity_name: Raw entity name from text

        Returns:
            Normalized canonical form
        """
        if not entity_name:
            return ""

        # Step 1: Clean and normalize structure
        normalized = entity_name.strip()
        normalized = re.sub(r'\s+', '_', normalized)  # spaces → underscores
        normalized = re.sub(r'[^\w\-]', '', normalized)  # remove special chars except dash

        # Step 2: Apply canonical case - split on underscores to preserve word boundaries
        if '_' in normalized:
            parts = normalized.split('_')
            normalized = '_'.join(part.capitalize() for part in parts if part)
        else:
            normalized = normalized.capitalize()

        return normalized

    def resolve_entity_name(self, entity_name: str) -> str:
        """
        Resolve an entity name to its canonical primary form.

        Args:
            entity_name: Original entity name from text

        Returns:
            Canonical primary name for the entity
        """
        if not entity_name:
            return entity_name

        entity_lower = entity_name.lower().strip()

        # Check predefined equivalences first
        if entity_lower in self.name_to_primary:
            return self.name_to_primary[entity_lower]

        # Check dynamic equivalences discovered in this document
        normalized = self._normalize_entity_name(entity_name)
        if normalized in self.dynamic_equivalences:
            return self.dynamic_equivalences[normalized]

        # No equivalence found, return normalized form
        return self._normalize_entity_name(entity_name)

    def get_all_equivalences(self) -> Dict[str, str]:
        """
        Get all known equivalences (predefined + dynamic) as mapping dict.

        Returns:
            Dict mapping alternative names to primary names
        """
        all_equivalences = dict(self.name_to_primary)
        all_equivalences.update(self.dynamic_equivalences)
        return all_equivalences

    def get_equivalence_report(self) -> Dict[str, Any]:
        """
        Generate a report of all discovered equivalences for analysis transparency.
        """
        return {
            "predefined_equivalences": len(self.predefined_equivalences),
            "dynamic_equivalences_discovered": len(self.dynamic_equivalences),
            "total_name_mappings": len(self.name_to_primary) + len(self.dynamic_equivalences),
            "dynamic_equivalences": dict(self.dynamic_equivalences),
            "predefined_primary_names": list(self.predefined_equivalences.keys())
        }