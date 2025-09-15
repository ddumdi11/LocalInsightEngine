"""
Shared neutralization utilities for statement extractors.

This module provides common neutralization logic to prevent code duplication
between different statement extractors while ensuring consistent behavior.
"""

import re
from typing import Optional


def is_sufficiently_neutralized(original: str, neutralized: str, threshold: float = 0.7) -> bool:
    """
    Check if neutralized version is sufficiently different from original.

    Args:
        original: Original text
        neutralized: Neutralized version
        threshold: Similarity threshold (0.0 = completely different, 1.0 = identical)
                  Default 0.7 means at least 30% different

    Returns:
        True if neutralized text is sufficiently different from original
    """
    original_words = set(original.lower().split())
    neutralized_words = set(neutralized.lower().split())

    if len(original_words) == 0:
        return False

    common_words = original_words.intersection(neutralized_words)
    similarity = len(common_words) / len(original_words)

    return similarity < threshold


def create_abstract_version(statement: str, language: str) -> str:
    """
    Create a highly abstract version of the statement with NO original content.

    CRITICAL: This method must NEVER include any original words or phrases
    to ensure copyright compliance and prevent canary phrases from leaking through.

    Args:
        statement: Original statement text
        language: Language ('german' or 'english')

    Returns:
        Completely abstract description without any original content
    """
    # Analyze statement characteristics without using original words
    has_numbers = bool(re.search(r'\d+(?:[.,]\d+)?%?', statement))
    has_research_indicators = False
    has_technical_content = False

    statement_lower = statement.lower()

    # Language-specific abstract fallbacks - NO ORIGINAL CONTENT
    if language == 'german':
        research_keywords = {'studie', 'forschung', 'daten', 'analyse', 'untersuchung', 'befund'}
        technical_keywords = {'system', 'methode', 'verfahren', 'prozess', 'technologie', 'algorithmus'}

        has_research_indicators = any(keyword in statement_lower for keyword in research_keywords)
        has_technical_content = any(keyword in statement_lower for keyword in technical_keywords)

        # Abstract templates with NO original content
        if has_numbers and has_research_indicators:
            return "Der Inhalt enthält quantitative Forschungsergebnisse."
        elif has_research_indicators:
            return "Der Inhalt beschreibt wissenschaftliche Erkenntnisse."
        elif has_technical_content:
            return "Der Inhalt behandelt technische Aspekte."
        elif has_numbers:
            return "Der Inhalt enthält numerische Informationen."
        else:
            return "Der Inhalt vermittelt sachliche Informationen."
    else:
        research_keywords = {'study', 'research', 'data', 'analysis', 'investigation', 'findings'}
        technical_keywords = {'system', 'method', 'process', 'technology', 'algorithm', 'technique'}

        has_research_indicators = any(keyword in statement_lower for keyword in research_keywords)
        has_technical_content = any(keyword in statement_lower for keyword in technical_keywords)

        # Abstract templates with NO original content
        if has_numbers and has_research_indicators:
            return "Content contains quantitative research findings."
        elif has_research_indicators:
            return "Content describes scientific insights."
        elif has_technical_content:
            return "Content addresses technical aspects."
        elif has_numbers:
            return "Content contains numerical information."
        else:
            return "Content conveys factual information."