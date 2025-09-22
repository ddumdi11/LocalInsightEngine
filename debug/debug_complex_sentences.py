#!/usr/bin/env python3
"""
Debug Complex Sentence Parsing - Analyze why conjunction and modal constructions fail
"""

import sys
# TODO: Replace with proper package installation or set PYTHONPATH environment variable
# instead of modifying sys.path. Install package with: pip install -e .
sys.path.append('src')
import spacy
from spacy.language import Language
from spacy.tokens import Doc
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def token_analysis(doc: Doc) -> None:
    """
    Analyze and log detailed token information including dependencies and relations.

    Args:
        doc: spaCy document object to analyze
    """
    logger.info("")
    logger.info("🔍 TOKEN ANALYSIS:")
    logger.info("Token      | Lemma    | POS   | Dep      | Head     | Children")
    logger.info("-" * 70)

    for token in doc:
        children = [child.text for child in token.children]
        logger.debug("%s | %s | %s | %s | %s | %s",
                    f"{token.text:10}", f"{token.lemma_:8}", f"{token.pos_:5}",
                    f"{token.dep_:8}", f"{token.head.text:8}", children)


def sentence_splitting(doc: Doc) -> None:
    """
    Analyze and log sentence boundaries detected by spaCy.

    Args:
        doc: spaCy document object to analyze
    """
    logger.info("")
    logger.info("📊 SENTENCE SPLITTING:")
    sentences = list(doc.sents)
    logger.info("Total sentences detected: %d", len(sentences))
    for i, sent in enumerate(sentences):
        logger.info("  Sentence %d: '%s'", i+1, sent.text.strip())


def root_analysis(doc: Doc) -> None:
    """
    Analyze root verbs and their syntactic relationships in each sentence.

    For each sentence, identifies the ROOT verb and analyzes:
    - Subjects (nsubj, sb, etc.)
    - Objects (dobj, oa, og, etc.)
    - Predicatives (attr, pd, etc.)
    - Conjunctions (conj, cd, etc.)
    - Modal/auxiliary verbs

    Args:
        doc: spaCy document object to analyze
    """
    logger.info("")
    logger.info("🎯 ROOT VERB ANALYSIS:")
    sentences = list(doc.sents)

    for i, sent in enumerate(sentences):
        logger.info("")
        logger.info("Sentence %d: '%s'", i+1, sent.text.strip())

        root_verb = None
        for token in sent:
            if token.dep_ == "ROOT":
                root_verb = token
                break

        if root_verb:
            logger.info("  ROOT: %s (POS: %s, Lemma: %s)", root_verb.text, root_verb.pos_, root_verb.lemma_)

            # Subject analysis
            subjects = []
            for child in root_verb.children:
                if child.dep_ in ["sb", "nsubj", "nsubjpass"]:  # German + English
                    subjects.append(child.text)
            logger.info("  Subjects: %s", subjects)

            # Object analysis
            objects = []
            for child in root_verb.children:
                if child.dep_ in ["oa", "og", "od", "dobj", "iobj"]:  # German + English
                    objects.append(child.text)
            logger.info("  Objects: %s", objects)

            # Copula predicative analysis
            predicatives = []
            for child in root_verb.children:
                if child.dep_ in ["pd", "attr"]:  # German + English
                    predicatives.append(child.text)
            logger.info("  Predicatives: %s", predicatives)

            # Conjunction analysis
            conjunctions = []
            for child in root_verb.children:
                if child.dep_ in ["cd", "conj"]:  # German + English
                    conjunctions.append(child.text)
            logger.info("  Conjunctions: %s", conjunctions)

            # Modal/auxiliary analysis
            modals = []
            for child in root_verb.children:
                if child.pos_ in ["AUX"] or child.dep_ in ["aux", "auxpass"]:
                    modals.append(child.text)
            logger.info("  Modals/Aux: %s", modals)
        else:
            logger.warning("  ❌ No ROOT found!")

def analyze_sentence_structure(nlp: Language, sentence: str) -> Doc:
    """
    Perform detailed analysis of sentence structure using spaCy.

    Analyzes tokens, dependencies, sentence splitting, and root verb patterns
    to understand complex German sentence constructions including conjunctions,
    modal verbs, and subordinate clauses.

    Args:
        nlp: Trained spaCy Language model for German text processing
        sentence: Input sentence text to analyze

    Returns:
        Doc: spaCy document object containing parsed sentence with linguistic annotations

    Logs:
        - Token analysis: word forms, lemmas, POS tags, dependencies, head relations
        - Sentence splitting: number of detected sentences and their boundaries
        - Root verb analysis: main verbs, subjects, objects, predicatives, conjunctions, modals
        - Warnings for sentences without detectable ROOT verbs
    """
    logger.info("")
    logger.info("="*60)
    logger.info("📝 ANALYZING: %s", sentence)
    logger.info("="*60)

    doc = nlp(sentence)

    # Perform modular analysis
    token_analysis(doc)
    sentence_splitting(doc)
    root_analysis(doc)

    return doc

def main() -> None:
    logger.info("🔍 COMPLEX SENTENCE PARSING DEBUG")
    logger.info("=" * 50)

    # Load German model (configurable via environment variable)
    model_name = os.getenv('SPACY_MODEL', 'de_core_news_sm')
    try:
        nlp = spacy.load(model_name)
        logger.info("✅ German spaCy model loaded: %s", model_name)
    except (OSError, ImportError) as e:
        logger.error("❌ Could not load German model '%s': %s", model_name, e)
        logger.error("Install with: python -m spacy download %s", model_name)
        logger.error("Or set SPACY_MODEL environment variable to a different model")
        sys.exit(1)
    # Test comprehensive German sentence patterns
    sentence_patterns = {
        "COORDINATING_CONJUNCTIONS": [
            # UND (additive)
            "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper.",
            "Vitamin B3 unterstützt den Stoffwechsel und fördert die Gesundheit.",

            # ODER (alternative)
            "Vitamin B3 ist wasserlöslich oder fettlöslich.",
            "Niacin kann oral oder intravenös gegeben werden.",

            # ABER (adversative)
            "Vitamin B3 ist wasserlöslich, aber schwer verdaulich.",
            "Niacin hilft bei Müdigkeit, aber kann Nebenwirkungen haben.",

            # SOWIE (additive)
            "Vitamin B3 unterstützt den Stoffwechsel sowie die Regeneration.",
        ],

        "SUBORDINATING_CONJUNCTIONS": [
            # WEIL (causal)
            "Vitamin B3 hilft, weil es den Stoffwechsel unterstützt.",
            "Der Körper braucht Niacin, weil es wichtig für Enzyme ist.",

            # DA (causal)
            "Vitamin B3 ist wichtig, da es wasserlöslich ist.",

            # OBWOHL (concessive)
            "Vitamin B3 wirkt gut, obwohl es wasserlöslich ist.",
            "Niacin hilft, obwohl die Dosis niedrig ist.",

            # WENN (conditional)
            "Vitamin B3 hilft, wenn es täglich eingenommen wird.",
            "Der Stoffwechsel funktioniert, wenn genug Niacin vorhanden ist.",

            # DASS (complement)
            "Studien zeigen, dass Vitamin B3 wichtig ist.",
            "Es ist bekannt, dass Niacin wasserlöslich ist.",
        ],

        "RELATIVE_CLAUSES": [
            # DAS/DIE/DER (restrictive)
            "Vitamin B3, das wasserlöslich ist, unterstützt den Körper.",
            "Niacin, das wichtig ist, hilft bei der Regeneration.",
            "Der Stoff, der als B3 bekannt ist, fördert die Gesundheit.",

            # WELCHES (non-restrictive)
            "Vitamin B3, welches wasserlöslich ist, unterstützt Enzyme.",
        ],

        "MODAL_CONSTRUCTIONS": [
            # KÖNNEN
            "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen.",
            "Niacin kann den Stoffwechsel unterstützen.",

            # SOLLEN
            "Vitamin B3 sollte täglich eingenommen werden.",
            "Niacin sollte mit Nahrung aufgenommen werden.",

            # MÜSSEN
            "Der Körper muss Vitamin B3 aufnehmen.",
            "Niacin muss regelmäßig zugeführt werden.",

            # DÜRFEN
            "Vitamin B3 darf nicht überdosiert werden.",
        ],

        "PASSIVE_CONSTRUCTIONS": [
            # WERDEN + PARTIZIP
            "Vitamin B3 wird vom Körper benötigt.",
            "Niacin wird schnell absorbiert.",
            "Der Stoffwechsel wird durch B3 unterstützt.",

            # SEIN + ZU + INFINITIV
            "Vitamin B3 ist täglich zu nehmen.",
            "Niacin ist gut zu vertragen.",
        ],

        "NEGATION_PATTERNS": [
            # NICHT
            "Vitamin B3 ist nicht fettlöslich.",
            "Niacin hilft nicht bei allen Problemen.",

            # OHNE
            "Ohne Niacin funktioniert der Stoffwechsel nicht.",
            "Ohne Vitamin B3 entstehen Mangelerscheinungen.",

            # KEIN
            "Es gibt keine Nebenwirkungen von Vitamin B3.",
            "Niacin hat keine negativen Effekte.",
        ],

        "DEEPLY_NESTED_CONSTRUCTIONS": [
            # Multiple subordinate clauses
            "Vitamin B3 hilft, weil es wichtig ist, obwohl die Dosis niedrig ist.",
            "Niacin wirkt, da es wasserlöslich ist, wenn es regelmäßig eingenommen wird.",

            # Relative + subordinate combinations
            "Das Vitamin, welches der Körper braucht, wenn er müde ist, heißt B3.",
            "Niacin, das wichtig ist, hilft, weil es den Stoffwechsel unterstützt.",

            # Nested relative clauses
            "Der Stoff, der als B3 bekannt ist, das wasserlöslich ist, unterstützt Enzyme.",
            "Vitamin B3, welches wichtig ist, das täglich benötigt wird, fördert Gesundheit.",

            # Complex coordinating + subordinating
            "Vitamin B3 ist wasserlöslich und hilft, weil es den Stoffwechsel unterstützt.",
            "Niacin wirkt gut, obwohl es wasserlöslich ist, und fördert die Regeneration.",

            # Modal + subordinate combinations
            "Vitamin B3 kann helfen, wenn es richtig dosiert wird, obwohl Nebenwirkungen möglich sind.",
            "Niacin sollte eingenommen werden, weil es wichtig ist, wenn der Körper es braucht.",

            # Passive + complex subordination
            "Vitamin B3 wird benötigt, weil es wichtig ist, obwohl es schnell ausgeschieden wird.",
            "Niacin wird absorbiert, wenn es mit Nahrung eingenommen wird, da es wasserlöslich ist.",

            # Triple nested constructions
            "Das Vitamin, das als B3 bekannt ist, hilft, weil es wasserlöslich ist, wenn genug davon vorhanden ist.",
            "Studien zeigen, dass Niacin, welches wichtig ist, wirkt, obwohl die Mechanismen unklar sind.",
        ],
    }

    # Also test some working sentences for comparison
    working_sentences = [
        "Vitamin B3 ist wasserlöslich.",  # Should work now
        "Niacin ist wichtig.",  # Should work now
        "Magnesium ist ein Mineral.",  # Should still work
    ]

    # Test all sentence patterns systematically
    logger.info("")
    logger.info("🧪 COMPREHENSIVE GERMAN SENTENCE PATTERN ANALYSIS:")
    logger.info("="*80)

    for category, sentences in sentence_patterns.items():
        logger.info("")
        logger.info(f"{'='*20} {category} {'='*20}")
        for i, sentence in enumerate(sentences, 1):
            logger.info("")
            logger.info(f"[{category} {i}/{len(sentences)}]")
            analyze_sentence_structure(nlp, sentence)

    logger.info("")
    logger.info("")
    logger.info("✅ REFERENCE: WORKING SIMPLE SENTENCES:")
    for sentence in working_sentences:
        analyze_sentence_structure(nlp, sentence)

    logger.info("")
    logger.info("="*60)
    logger.info("🧪 PATTERN ANALYSIS SUMMARY:")
    logger.info("="*60)

    logger.info("")
    logger.info("📊 COMPREHENSIVE ANALYSIS RESULTS:")
    logger.info("This analysis covers ALL major German sentence patterns:")
    logger.info("• Coordinating Conjunctions: UND, ODER, ABER, SOWIE")
    logger.info("• Subordinating Conjunctions: WEIL, DA, OBWOHL, WENN, DASS")
    logger.info("• Relative Clauses: DAS/DIE/DER, WELCHES")
    logger.info("• Modal Constructions: KÖNNEN, SOLLEN, MÜSSEN, DÜRFEN")
    logger.info("• Passive Constructions: WERDEN + Partizip, SEIN + ZU")
    logger.info("• Negation Patterns: NICHT, OHNE, KEIN")
    logger.info("• Deeply Nested Constructions: Multiple subordinate/relative clause combinations")

    logger.info("")
    logger.info("🎯 KEY INSIGHTS FOR TRIPLE EXTRACTION:")
    logger.info("1. Which patterns are parsed correctly by spaCy de_core_news_lg?")
    logger.info("2. Which sentence structures need custom extraction logic?")
    logger.info("3. How do different conjunctions affect dependency parsing?")
    logger.info("4. What ROOT detection patterns work vs. fail?")

    logger.info("")
    logger.info("💡 USE THIS DATA TO:")
    logger.info("• Plan targeted TDD cycles for specific sentence patterns")
    logger.info("• Identify which constructions need Extractor enhancements")
    logger.info("• Prioritize the most important German grammatical structures")
    logger.info("• Design comprehensive test cases for semantic triple extraction")

if __name__ == "__main__":
    main()