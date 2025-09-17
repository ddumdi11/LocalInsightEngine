"""
Real Claude API client for Layer 3 analysis.
LocalInsightEngine v0.1.0 - Layer 3: Analysis Engine
"""

import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

import anthropic
from anthropic import Anthropic

from ...models.text_data import ProcessedText
from ...models.analysis import AnalysisResult, Insight, Question
from ...config.settings import Settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Real Claude API client for external analysis.
    
    Sends neutralized content to Claude for deep analysis while maintaining
    copyright compliance by never transmitting original text.
    """
    
    def __init__(self, settings: Optional[Settings] = None, debug_logging: bool = False):
        self.settings = settings or Settings()
        self.debug_logging = debug_logging
        self.client = None
        self._initialize_client()
        
        # Analysis prompts
        self.system_prompt = """Du bist ein Experte für die Analyse von Sachbüchern und Dokumenten. 
Du erhältst neutralisierte, urheberrechtsfreie Daten aus Texten und sollst daraus tiefgreifende Einsichten generieren.

Wichtige Hinweise:
- Du erhältst niemals den Originaltext, sondern nur neutralisierte Zusammenfassungen
- Fokussiere auf Muster, Zusammenhänge und Schlussfolgerungen
- Identifiziere Widersprüche und Wissenslücken
- Stelle kluge Nachfragen zur Vertiefung des Verständnisses
- Antworte auf Deutsch

Deine Aufgabe: Erstelle aus den neutralisierten Daten eine strukturierte Analyse mit:
1. Haupterkenntnissen (Insights)
2. Wichtigen Mustern und Beziehungen
3. Identifizierten Widersprüchen
4. Intelligenten Nachfragen für weitere Analysen
5. Zusammenfassung der Kernthemen"""

        self.analysis_prompt = """Analysiere die folgenden neutralisierten Textdaten:

=== DATEN ===
{content}

=== THEMEN ===
{themes}

=== STATISTIKEN ===
Chunks: {chunk_count}, Entitäten: {entity_count}

Erstelle eine Analyse im JSON-Format:

{{
  "executive_summary": "Haupterkenntnisse in 2-3 Sätzen",
  "main_insights": [
    {{
      "title": "Erkenntnis-Titel",
      "content": "Beschreibung",
      "confidence": 0.8
    }}
  ],
  "follow_up_questions": []
}}

Antworte NUR mit validem JSON, keine zusätzlichen Erklärungen."""

    def _initialize_client(self):
        """Initialize Claude API client."""
        if not self.settings.llm_api_key:
            logger.warning("No Claude API key provided. Set LLM_API_KEY environment variable.")
            return
        
        try:
            self.client = Anthropic(
                api_key=self.settings.llm_api_key,
                base_url=self.settings.llm_base_url
            )
            logger.info("Claude API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            self.client = None

    def analyze(self, processed_text: ProcessedText) -> Dict[str, Any]:
        """
        Analyze processed text using Claude API.

        Args:
            processed_text: Neutralized text from Layer 2

        Returns:
            Analysis results from Claude
        """
        if not self.client:
            logger.warning("Claude client not available, returning mock analysis")
            return self._mock_analysis(processed_text)

        start_time = datetime.now()

        # DEBUG: Log analysis details (only when explicitly enabled to prevent PII leaks)
        if self.debug_logging:
            logger.debug(f"=== DEBUGGING PROCESSED TEXT ===")
            logger.debug(f"ProcessedText chunks count: {len(processed_text.chunks)}")
            logger.debug(f"ProcessedText total_chunks: {processed_text.total_chunks}")
            logger.debug(f"ProcessedText all_entities count: {len(processed_text.all_entities)}")
            logger.debug(f"ProcessedText total_entities: {processed_text.total_entities}")
            logger.debug(f"ProcessedText key_themes: {processed_text.key_themes}")
            logger.debug(f"First chunk sample: {processed_text.chunks[0] if processed_text.chunks else 'NO CHUNKS'}")
            if processed_text.chunks:
                # Mask potential PII in content while preserving structure info
                content_preview = processed_text.chunks[0].neutralized_content[:200] if processed_text.chunks[0].neutralized_content else 'EMPTY NEUTRALIZED_CONTENT'
                masked_content = self._mask_potential_pii(content_preview)
                logger.debug(f"First chunk neutralized_content: {masked_content}")
                logger.debug(f"First chunk key_statements: {processed_text.chunks[0].key_statements}")
            logger.debug(f"=== END DEBUG ===")
        else:
            # Safe logging for production - no content, just statistics
            logger.info(f"Processing {len(processed_text.chunks)} chunks with {len(processed_text.all_entities)} entities")

        try:
            # Prepare content for Claude
            content = self._prepare_content(processed_text)

            # Call Claude API
            response = self.client.messages.create(
                model=self.settings.llm_model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent analysis
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            # Parse response
            analysis_result = self._parse_claude_response(
                response.content[0].text,
                processed_text,
                start_time
            )
            
            logger.info(f"Claude analysis completed successfully in {(datetime.now() - start_time).total_seconds():.2f}s")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return self._mock_analysis(processed_text)

    def answer_question(self, processed_text: ProcessedText, question: str) -> str:
        """
        Answer a specific question about processed text using Claude API.

        Args:
            processed_text: Neutralized text from Layer 2
            question: User's question about the content

        Returns:
            Direct answer string (not full analysis structure)
        """
        if not self.client:
            return "Analysis service not available. Please check API configuration."

        start_time = datetime.now()

        # Safe logging for Q&A - mask question to prevent PII leaks
        if self.debug_logging:
            # Only log full question details when explicitly enabled
            logger.debug(f"Processing Q&A for {len(processed_text.chunks)} chunks, question: {self._mask_potential_pii(question)}")
        else:
            # Production safe logging - no question content
            logger.info(f"Processing Q&A for {len(processed_text.chunks)} chunks")

        try:
            # Prepare focused content for Q&A
            context = self._prepare_qa_content(processed_text, question)

            # Specialized Q&A prompt
            qa_prompt = f"""Du bist ein präziser Assistent für Dokumentenanalyse.

Beantworte die Frage des Nutzers basierend AUSSCHLIESSLICH auf dem bereitgestellten neutralisierten Inhalt.

WICHTIG:
- Antworte nur mit Informationen aus dem bereitgestellten Text
- Falls die Information nicht vorhanden ist, sage das ehrlich
- Halte die Antwort präzise und sachlich
- Keine Spekulationen oder externes Wissen

NEUTRALISIERTER INHALT:
{context}

FRAGE: {question}

ANTWORT:"""

            # Call Claude API for Q&A
            response = self.client.messages.create(
                model=self.settings.llm_model,
                max_tokens=1000,  # Shorter for Q&A
                temperature=0.1,  # Very low for factual answers
                messages=[
                    {
                        "role": "user",
                        "content": qa_prompt
                    }
                ]
            )

            answer = response.content[0].text.strip()

            logger.info(f"Q&A completed successfully in {(datetime.now() - start_time).total_seconds():.2f}s")
            return answer

        except Exception as e:
            logger.error(f"Q&A failed: {e}")
            return f"Sorry, I could not process your question due to a technical error."

    def _prepare_qa_content(self, processed_text: ProcessedText, question: str) -> str:
        """Prepare focused content for Q&A (different from full analysis)."""

        # Smart chunk selection based on question keywords
        question_lower = question.lower()
        question_words = [word for word in question_lower.split() if len(word) > 2]

        relevant_chunks = []

        # Search for relevant chunks
        for chunk in processed_text.chunks[:100]:  # Search first 100 chunks
            if chunk.neutralized_content:
                content_lower = chunk.neutralized_content.lower()
                # Score chunks by keyword relevance
                score = sum(1 for word in question_words if word in content_lower)
                if score > 0:
                    relevant_chunks.append((score, chunk.neutralized_content[:400]))

        # Sort by relevance and take top chunks
        relevant_chunks.sort(key=lambda x: x[0], reverse=True)
        selected_content = [content for score, content in relevant_chunks[:5]]

        # Fallback to first chunks if no relevant content found
        if not selected_content:
            selected_content = [
                chunk.neutralized_content[:400]
                for chunk in processed_text.chunks[:3]
                if chunk.neutralized_content
            ]

        return "\n\n".join(selected_content)

    def _prepare_content(self, processed_text: ProcessedText) -> str:
        """Prepare neutralized content for Claude analysis."""

        # Sample key statements from chunks
        key_statements = []
        chunk_contents = []

        for chunk in processed_text.chunks[:20]:  # Limit to first 20 chunks
            # Get key statements if available
            if chunk.key_statements:
                key_statements.extend(chunk.key_statements[:3])  # Max 3 per chunk
            # Also get chunk content as fallback
            if hasattr(chunk, 'neutralized_content') and chunk.neutralized_content:
                chunk_contents.append(chunk.neutralized_content[:200])  # First 200 chars
            elif hasattr(chunk, 'content') and chunk.content:
                chunk_contents.append(chunk.content[:200])  # First 200 chars

        # Prepare entity summary
        entity_summary = self._summarize_entities(processed_text.all_entities)

        # Entity type statistics
        entity_types = {}
        for entity in processed_text.all_entities:
            entity_types[entity.label] = entity_types.get(entity.label, 0) + 1

        # Combine all available content
        all_content = []
        if key_statements:
            all_content.extend(key_statements[:30])
        if chunk_contents and not key_statements:
            all_content.extend(chunk_contents[:15])  # Fallback to chunk content

        # Debug logging
        logger.debug(f"Content preparation: {len(key_statements)} statements, {len(chunk_contents)} chunks, {len(all_content)} total items")
        logger.debug(f"Sample content: {all_content[:2] if all_content else 'NO CONTENT'}")

        content = self.analysis_prompt.format(
            content="\n".join(all_content),
            themes=", ".join(processed_text.key_themes),
            chunk_count=processed_text.total_chunks,
            entity_count=processed_text.total_entities
        )

        return content

    def _mask_potential_pii(self, text: str) -> str:
        """
        Mask potential PII in log output for privacy protection.

        Args:
            text: Text that might contain personal information

        Returns:
            Text with potential PII masked but structure preserved
        """
        import re

        # Don't mask if text is too short
        if len(text) < 20:
            return text

        # Mask potential questions that might contain personal info
        if "?" in text:
            return "[QUESTION_CONTENT_MASKED_FOR_PRIVACY]"

        # Mask potential personal names (sequences of capitalized words)
        masked = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', '[NAME]', text)

        # Mask potential email addresses
        masked = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', masked)

        # Mask potential phone numbers
        masked = re.sub(r'\b\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b', '[PHONE]', masked)

        return masked[:200] + ("..." if len(text) > 200 else "")

    def _summarize_entities(self, entities: List) -> str:
        """Create a summary of entities by type."""
        entity_groups = {}
        
        for entity in entities[:100]:  # Limit to first 100 entities
            if entity.label not in entity_groups:
                entity_groups[entity.label] = []
            if len(entity_groups[entity.label]) < 10:  # Max 10 per type
                entity_groups[entity.label].append(entity.text)
        
        summary_lines = []
        for entity_type, entity_list in entity_groups.items():
            summary_lines.append(f"{entity_type}: {', '.join(entity_list)}")
        
        return "\n".join(summary_lines)

    def _parse_claude_response(self, response_text: str, processed_text: ProcessedText, start_time: datetime) -> Dict[str, Any]:
        """Parse Claude's JSON response into our analysis format."""
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                claude_analysis = json.loads(json_text)
            else:
                # If no JSON found, create structured response from text
                claude_analysis = self._extract_from_text(response_text)
            
            # Convert to our analysis format
            analysis_result = {
                "status": "success",
                "model": self.settings.llm_model,
                "analysis_timestamp": start_time.isoformat(),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "executive_summary": claude_analysis.get("executive_summary", "Analyse durchgeführt"),
                "insights": claude_analysis.get("main_insights", []),
                "questions": claude_analysis.get("follow_up_questions", []),
                "key_relationships": claude_analysis.get("key_relationships", {}),
                "contradictions": claude_analysis.get("contradictions", []),
                "knowledge_gaps": claude_analysis.get("knowledge_gaps", []),
                "recommendations": claude_analysis.get("recommendations", []),
                "themes": processed_text.key_themes,
                "entity_analysis": {
                    "total_entities": processed_text.total_entities,
                    "entity_types": len(set(e.label for e in processed_text.all_entities))
                },
                "confidence_score": self._calculate_confidence(claude_analysis),
                "completeness_score": self._calculate_completeness(claude_analysis)
            }
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Claude JSON response: {e}")
            logger.debug(f"Response text excerpt: {response_text[:200]}...")
            return self._create_text_analysis(response_text, processed_text, start_time)
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            logger.debug(f"Raw response: {response_text[:300]}...")
            return self._create_text_analysis(response_text, processed_text, start_time)

    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from plain text response."""
        return {
            "executive_summary": text[:200] + "..." if len(text) > 200 else text,
            "main_insights": [
                {
                    "title": "Claude Analyse",
                    "content": text,
                    "confidence": 0.7,
                    "category": "synthesis"
                }
            ],
            "follow_up_questions": [],
            "contradictions": [],
            "knowledge_gaps": [],
            "recommendations": []
        }

    def _create_text_analysis(self, response_text: str, processed_text: ProcessedText, start_time: datetime) -> Dict[str, Any]:
        """Create analysis from plain text response."""
        return {
            "status": "success",
            "model": self.settings.llm_model,
            "analysis_timestamp": start_time.isoformat(),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
            "executive_summary": response_text[:300] + "..." if len(response_text) > 300 else response_text,
            "insights": [
                {
                    "title": "Claude Textanalyse",
                    "content": response_text,
                    "confidence": 0.8,
                    "category": "synthesis"
                }
            ],
            "questions": [],
            "key_relationships": {},
            "contradictions": [],
            "knowledge_gaps": [],
            "recommendations": [],
            "themes": processed_text.key_themes,
            "confidence_score": 0.7,
            "completeness_score": 0.8
        }

    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence score based on analysis completeness."""
        factors = [
            len(analysis.get("main_insights", [])) > 0,
            len(analysis.get("executive_summary", "")) > 50,
            len(analysis.get("follow_up_questions", [])) > 0,
            len(analysis.get("key_relationships", {})) > 0
        ]
        return sum(factors) / len(factors)

    def _calculate_completeness(self, analysis: Dict) -> float:
        """Calculate completeness score."""
        sections = [
            "executive_summary", "main_insights", "follow_up_questions", 
            "key_relationships", "contradictions", "recommendations"
        ]
        completed = sum(1 for section in sections if analysis.get(section))
        return completed / len(sections)

    def _mock_analysis(self, processed_text: ProcessedText) -> Dict[str, Any]:
        """Fallback mock analysis when Claude API is not available."""
        return {
            "status": "mock",
            "model": "mock-fallback",
            "executive_summary": f"Mock-Analyse für Dokument mit {processed_text.total_chunks} Chunks und {processed_text.total_entities} Entitäten.",
            "insights": [
                {
                    "title": "Mock Insight",
                    "content": "Dies ist eine Mock-Analyse. Für echte Analyse Claude API-Key setzen.",
                    "confidence": 0.5,
                    "category": "mock"
                }
            ],
            "questions": [],
            "themes": processed_text.key_themes,
            "confidence_score": 0.5,
            "completeness_score": 0.3
        }