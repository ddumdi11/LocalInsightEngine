"""
Main entry point for LocalInsightEngine application.
"""

import logging
import configparser
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .config.settings import Settings
from .services.data_layer.document_loader import DocumentLoader
from .services.processing_hub.text_processor import TextProcessor
from .services.analysis_engine.claude_client import ClaudeClient
from .services.export.export_manager import ExportManager
from .persistence.database import get_database_manager
from .utils.debug_logger import debug_logger
from .utils.question_router import QuestionRouter, QuestionCategory
from .models.processing_config import ProcessingConfig

# Use enhanced debug logger instead of basic logging
logger = debug_logger


class LocalInsightEngine:
    """Main application class for LocalInsightEngine."""

    def __init__(self, settings: Optional[Settings] = None):
        # Initialize enhanced logging
        logger.step("Initializing LocalInsightEngine", {
            "version": "0.1.1",
            "settings": "custom" if settings else "default"
        })

        self.settings = settings or Settings()

        # Load configuration file
        self.config = configparser.ConfigParser()
        config_path = Path("localinsightengine.conf")
        if config_path.exists():
            self.config.read(config_path, encoding='utf-8')

        # Initialize database manager for persistence
        try:
            self.db_manager = get_database_manager()
            logger.database_operation("Database initialized", {
                "db_path": str(self.db_manager.db_path),
                "health_check": self.db_manager.health_check()
            })
        except Exception as e:
            logger.error("Failed to initialize database", e)
            self.db_manager = None

        # Initialize service layers
        self.document_loader = DocumentLoader()
        self.text_processor = TextProcessor()
        self.llm_client = ClaudeClient(self.settings)
        self.export_manager = ExportManager()
        self.question_router = QuestionRouter()

        # Store processed data for Q&A (legacy fallback)
        self.last_processed_data = None
        self.last_analysis_result = None

        # Test dependencies
        logger.test_dependencies()

        logger.info("LocalInsightEngine initialized successfully")
    
    def analyze_document_with_config(self, document_path: Path, config: ProcessingConfig = None) -> dict:
        """
        Analyze a document with ProcessingConfig (new architecture).

        Args:
            document_path: Path to the document to analyze
            config: ProcessingConfig object (defaults to standard mode)

        Returns:
            Analysis results dictionary
        """
        if config is None:
            config = ProcessingConfig.standard_mode()

        logger.performance_start("document_analysis")
        logger.step("Starting document analysis", {
            "document": str(document_path),
            "processing_config": config.to_dict(),
            "file_size": document_path.stat().st_size if document_path.exists() else "N/A"
        })

        try:
            # Layer 1: Load document
            logger.performance_start("document_loading")
            document = self.document_loader.load(document_path)
            logger.performance_end("document_loading", {
                "document_id": str(document.id),
                "pages": len(document.page_mapping),
                "paragraphs": len(document.paragraph_mapping),
                "characters": len(document.text_content)
            })

            # Layer 2: Process and neutralize content
            logger.performance_start("text_processing")
            processed_data = self.text_processor.process_with_config(document, config)
            logger.performance_end("text_processing", {
                "chunks_created": len(processed_data.chunks),
                "entities_extracted": len(processed_data.all_entities) if hasattr(processed_data, 'all_entities') else 0,
                "processing_mode": config.processing_mode.value
            })

            # Log detailed chunk information
            logger.debug("Text processing completed", {
                "total_chunks": len(processed_data.chunks),
                "total_entities": len(processed_data.all_entities) if hasattr(processed_data, 'all_entities') else 0,
                "key_themes": len(processed_data.key_themes),
                "processing_time": processed_data.processing_time_seconds
            })

            # Layer 3: Analyze with LLM
            logger.performance_start("llm_analysis")
            analysis = self.llm_client.analyze(processed_data)
            logger.performance_end("llm_analysis", {
                "status": analysis.get("status", "unknown"),
                "insights_count": len(analysis.get("insights", [])),
                "questions_count": len(analysis.get("questions", []))
            })

            # Store analysis statistics for GUI access
            self.last_analysis_statistics = self.text_processor.get_analysis_statistics()

            # Persist analysis results to database for future Q&A sessions
            if self.db_manager:
                try:
                    # Extract factual mode from config for persistence
                    factual_mode = config.is_factual_mode
                    self._persist_analysis(document_path, processed_data, analysis, factual_mode)
                    logger.info("✅ Analysis successfully persisted to database")
                except Exception as e:
                    logger.error("Failed to persist analysis to database: %s", e)
                    # Log additional context for debugging
                    logger.error("Document path: %s, Factual mode: %s", document_path, config.is_factual_mode)
                    # Note: Database session cleanup is handled by the repository pattern

            result = {
                'analysis': analysis,
                'statistics': {
                    'chunks': len(processed_data.chunks),
                    'entities': len(processed_data.all_entities) if hasattr(processed_data, 'all_entities') else 0,
                    'themes': len(processed_data.key_themes),
                    'processing_time': processed_data.processing_time_seconds
                },
                'processing_config': config.to_dict()
            }

            logger.info("Document analysis completed successfully")
            return result

        except Exception as e:
            logger.error("Document analysis failed", e, {
                "document": str(document_path),
                "processing_config": config.to_dict()
            })
            raise
        finally:
            logger.performance_end("document_analysis")

    def analyze_document(self, document_path: Path, factual_mode: bool = False) -> dict:
        """
        Analyze a document through the 3-layer architecture (legacy API).

        DEPRECATED: Use analyze_document_with_config() for new code.
        This method is maintained for backward compatibility.

        Args:
            document_path: Path to the document to analyze
            factual_mode: If True, disables anonymization of common factual terms

        Returns:
            Analysis results dictionary
        """
        # Convert legacy parameter to ProcessingConfig
        config = ProcessingConfig.from_legacy_params(factual_mode=factual_mode)

        # Add deprecation warning to logs
        logger.info("DEPRECATED: analyze_document(factual_mode) called. Use analyze_document_with_config() for new code.")

        # Delegate to new implementation
        result = self.analyze_document_with_config(document_path, config)

        # Remove ProcessingConfig from result for backward compatibility
        if 'processing_config' in result:
            del result['processing_config']

        return result
        logger.performance_start("document_analysis")
        logger.step("Starting document analysis", {
            "document": str(document_path),
            "factual_mode": factual_mode,
            "file_size": document_path.stat().st_size if document_path.exists() else "N/A"
        })

        try:
            # Layer 1: Load document
            logger.performance_start("document_loading")
            document = self.document_loader.load(document_path)
            logger.performance_end("document_loading", {
                "format": document.metadata.file_format,
                "content_length": len(document.text_content)
            })
            logger.file_info(document_path, "Source document")

            # Layer 2: Process and neutralize content
            logger.performance_start("text_processing")
            processed_data = self.text_processor.process(document, bypass_anonymization=factual_mode)
            logger.performance_end("text_processing", {
                "chunks_created": len(processed_data.chunks),
                "entities_extracted": len(processed_data.all_entities) if hasattr(processed_data, 'all_entities') else 0,
                "bypass_anonymization": factual_mode
            })

            # Log detailed chunk information
            for i, chunk in enumerate(processed_data.chunks[:5]):  # First 5 chunks
                logger.chunk_details(f"chunk_{i}", {
                    "id": str(chunk.id),
                    "word_count": chunk.word_count,
                    "content_preview": chunk.neutralized_content[:100] if chunk.neutralized_content else "N/A"
                })

            # Layer 3: Analyze with LLM
            logger.performance_start("llm_analysis")
            analysis = self.llm_client.analyze(processed_data)
            logger.performance_end("llm_analysis")

            # Re-enable analysis persistence for Q&A functionality
            if self.db_manager:
                try:
                    self._persist_analysis(document_path, processed_data, analysis, factual_mode)
                    logger.info("✅ Analysis successfully persisted to database")
                except Exception as e:
                    logger.error("Failed to persist analysis to database", e)
                    # Continue execution - persistence failure shouldn't break Q&A

            # Store for Q&A (legacy fallback)
            self.last_processed_data = processed_data
            self.last_analysis_result = analysis

            # Store comprehensive statistics for analysis report
            self.last_analysis_statistics = self.text_processor.get_analysis_statistics()

            logger.step("Analysis completed successfully")
            return analysis

        except Exception as e:
            logger.error("Document analysis failed", e, {
                "document": str(document_path),
                "factual_mode": factual_mode
            })
            raise
        finally:
            logger.performance_end("document_analysis")

    def _persist_analysis(self, document_path: Path, processed_data, analysis: dict, factual_mode: bool):
        """Persist analysis results to database for future Q&A sessions"""
        try:
            from datetime import datetime
            import json
            from .persistence.repository import SessionRepository

            logger.database_operation("Persisting analysis results")

            repo = SessionRepository(self.db_manager.get_session())
            # CRITICAL FIX: Combine ALL chunks' content for FTS5 search
            # In factual mode, use original content for better Q&A quality
            # Previous version only stored first chunk - caused 0 search results!

            # COPYRIGHT COMPLIANCE: ALWAYS use neutralized content for storage and external APIs
            # Original content must NEVER be stored or sent to external services
            searchable_context = ""
            if processed_data.chunks:
                all_chunk_content = []
                for i, chunk in enumerate(processed_data.chunks):
                    if chunk.neutralized_content:
                        chunk_header = f"=== Chunk {i+1}/{len(processed_data.chunks)} ==="
                        all_chunk_content.append(f"{chunk_header}\n{chunk.neutralized_content}")
                searchable_context = "\n\n".join(all_chunk_content)

                # Log the storage mode for transparency
                mode_label = "FACTUAL" if factual_mode else "STANDARD"
                logger.info(f"Combined {len(processed_data.chunks)} chunks into {mode_label} NEUTRALIZED searchable content ({len(searchable_context)} chars)")
            created = repo.create_session(
                document_path=document_path,
                analysis_result=analysis,
                neutralized_context=searchable_context,
            )
            logger.info("Analysis persisted", {
                "session_id": getattr(created, "session_id", None),
                "chunk_count": len(processed_data.chunks)
            })

        except Exception as e:
            logger.error("Failed to persist analysis", e)
            raise

    def answer_question(self, question: str) -> str:
        """
        Answer a question about the last analyzed document using enhanced search.

        Args:
            question: Question to answer

        Returns:
            Answer based on neutralized document content or general knowledge
        """

        # Smart question routing: Determine optimal processing strategy
        routing = self.question_router.route_question(question)

        logger.debug("Question routing analysis", {
            "category": routing.category.value,
            "template_type": routing.template_type,
            "needs_document": routing.needs_document,
            "allow_external_knowledge": routing.allow_external_knowledge,
            "confidence": routing.confidence,
            "reasoning": routing.reasoning
        })

        if routing.category == QuestionCategory.GENERAL_KNOWLEDGE:
            # Pure general knowledge - no document context needed
            return self._handle_general_knowledge_question(question)

        # Continue with document-aware Q&A (includes list, explain, and hybrid modes)
        logger.performance_start("qa_session")
        logger.step("Processing Q&A question", {"question": question})

        if not self.last_processed_data and not self.db_manager:
            logger.warning("No document data available for Q&A and no database connection")
            return "No document has been analyzed yet. Please analyze a document first."

        # If no in-memory data but database available, try to use database search
        if not self.last_processed_data and self.db_manager:
            logger.info("No in-memory data, attempting database-only Q&A search")
            try:
                # Try database search directly
                relevant_chunks, search_method = self._search_with_fts5(question)
                if not relevant_chunks:
                    logger.warning("No relevant content found in database for Q&A")
                    return "No relevant content found for your question. Please analyze a document first."
            except Exception as e:
                logger.error("Database Q&A search failed", e)
                return "Unable to search document database. Please analyze a document first."

        try:
            # Enhanced search: Try FTS5 if database is available, fallback to keyword matching
            # (Skip if already done in database-only mode above)
            if not ('relevant_chunks' in locals() and relevant_chunks):
                relevant_chunks = []
                search_method = "unknown"

                if self.db_manager:
                    try:
                        relevant_chunks, search_method = self._search_with_fts5(question)
                    except Exception as e:
                        logger.warning("FTS5 search failed, falling back to keyword matching", e)
                        if self.last_processed_data:  # Only fallback if we have in-memory data
                            relevant_chunks, search_method = self._search_with_keywords(question)
                elif self.last_processed_data:
                    relevant_chunks, search_method = self._search_with_keywords(question)

            logger.debug("Search completed", {
                "method": search_method,
                "chunks_found": len(relevant_chunks),
                "question": question
            })

            # If no relevant chunks found, use first few chunks as context (only if in-memory data available)
            if not relevant_chunks and self.last_processed_data:
                relevant_chunks = [
                    chunk.neutralized_content[:300]
                    for chunk in self.last_processed_data.chunks[:10]
                    if chunk.neutralized_content
                ]
                search_method = "fallback_first_chunks"
                logger.debug("Using fallback chunks", {"chunk_count": len(relevant_chunks)})
            elif not relevant_chunks:
                # No chunks found and no in-memory data
                logger.warning("No relevant chunks found and no fallback data available")
                return "No relevant content found for your question."

            # Create context from relevant chunks
            context = "\n".join(relevant_chunks[:5])  # Max 5 chunks

            # Create ProcessedText with raw context chunks (no pre-formatting!)
            from .models.text_data import ProcessedText, TextChunk

            # Use document ID from memory or generate fallback for database-only mode
            doc_id = (self.last_processed_data.source_document_id
                     if self.last_processed_data
                     else uuid4())

            # Create chunks from raw context - let claude_client handle template formatting
            context_chunks = []
            for i, chunk_text in enumerate(relevant_chunks[:5]):  # Max 5 chunks
                context_chunks.append(TextChunk(
                    id=uuid4(),
                    neutralized_content=chunk_text,
                    source_document_id=doc_id,
                    original_char_range=(i * 1000, (i + 1) * 1000),  # Approximate ranges
                    word_count=len(chunk_text.split())
                ))

            qa_processed = ProcessedText(
                id=uuid4(),
                source_document_id=doc_id,
                chunks=context_chunks,
                total_chunks=len(context_chunks),
                total_entities=0,  # Will be filled by claude_client if needed
                key_themes=[]  # Will be filled by claude_client if needed
            )

            # Use dedicated Q&A method for better results
            logger.performance_start("llm_qa")
            try:
                # ALWAYS use the specialized Q&A method with new template
                if hasattr(self.llm_client, 'answer_question'):
                    # Use database content for Q&A (qa_processed contains search results)
                    answer = self.llm_client.answer_question(qa_processed, question, routing.template_type)
                else:
                    # Fallback to general analysis method (should not happen)
                    result = self.llm_client.analyze(qa_processed)
                    if isinstance(result, dict):
                        answer = (result.get('executive_summary') or
                               str(result.get('insights', 'No answer available')))
                    else:
                        answer = str(result)

                logger.performance_end("llm_qa")

                # Log Q&A session details
                logger.qa_session(question, answer, len(relevant_chunks))

                # Persist Q&A exchange if database is available
                if self.db_manager:
                    try:
                        self._persist_qa_exchange(question, answer, context, search_method)
                    except Exception as e:
                        logger.error("Failed to persist Q&A exchange", e)

                logger.performance_end("qa_session")
                return answer

            except Exception as e:
                logger.error("answer_question failed", e)
                return "Sorry, I could not process your question due to a technical error."

        except Exception as e:
            logger.error("Q&A session failed", e, {"question": question})
            return "Sorry, I could not process your question due to a technical error."
    def analyze_and_export(
        self,
        document_path: Path,
        output_path: Optional[Path] = None,
        formats: Optional[list] = None,
        factual_mode: bool = False
    ) -> dict:
        """
        Analyze a document and export results in specified formats.
        
        Args:
            document_path: Path to the document to analyze
            output_path: Path for export files (without extension)
            formats: List of export formats (default: ["json"])
            factual_mode: If True, disables anonymization for scientific/factual content
            
        Returns:
            Dictionary with analysis results and export status
        """
        if formats is None:
            formats = ["json"]
            
        logger.info(f"Starting analysis and export of document: {document_path}")
        
        # Layer 1: Load document
        document = self.document_loader.load(document_path)
        
        # Layer 2: Process and neutralize content
        processed_data = self.text_processor.process(document, bypass_anonymization=factual_mode)
        
        # Layer 3: Analyze with LLM
        analysis = self.llm_client.analyze(processed_data)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = self.export_manager.generate_output_filename(document)
        
        # Export results
        export_results = self.export_manager.export_analysis(
            analysis, processed_data, document, output_path, formats, factual_mode
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
            analysis_result, processed_text, document, output_path, formats, False
        )

    def _search_with_fts5(self, question: str) -> tuple[list[str], str]:
        """Search using session content and FTS5 semantic search in database."""
        try:
            from .persistence.repository import SessionRepository
            from .persistence.models import PersistentQASession
            from sqlalchemy import desc

            repo = SessionRepository(self.db_manager.get_session())
            session = repo._get_session()

            # First, try to find content in the latest session
            latest_session = session.query(PersistentQASession).order_by(desc(PersistentQASession.created_at)).first()

            if latest_session and latest_session.neutralized_context:
                # Search the session content for relevant chunks
                session_content = latest_session.neutralized_context
                relevant_chunks = self._search_session_content(question, session_content)

                if relevant_chunks:
                    logger.debug("Session content search results", {
                        "query": question,
                        "results_count": len(relevant_chunks),
                        "method": "session_content_search"
                    })
                    return relevant_chunks, "session_content_search"

            # Fallback: Try FTS5 search for Q&A exchanges (previous questions)
            search_results = repo.search_qa_content(
                query=question,
                limit=10,
                time_decay_weight=0.2,
                min_score=0.1
            )

            logger.debug("FTS5 search results", {
                "query": question,
                "results_count": len(search_results),
                "method": "fts5_semantic_search"
            })

            if search_results:
                # Extract relevant content from search results
                relevant_chunks = []
                for result in search_results[:5]:  # Top 5 results
                    # Use the answer from previous Q&A as context
                    chunk_content = f"Q: {result.question}\nA: {result.answer}"
                    relevant_chunks.append(chunk_content[:400])  # Limit length

                return relevant_chunks, "fts5_semantic_search"
            else:
                # No results in either session content or FTS5
                return [], "no_results"

        except Exception as e:
            logger.error("FTS5 search failed", e)
            raise

    def _search_session_content(self, question: str, session_content: str) -> list[str]:
        """Search within session content for relevant chunks."""
        if not session_content:
            return []

        # Split session content into chunks (they're already separated by headers)
        chunks = []
        current_chunk = ""

        for line in session_content.split('\n'):
            if line.startswith('=== Chunk '):
                # Start new chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = ""
            else:
                current_chunk += line + '\n'

        # Add last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Search for relevant chunks using keyword matching with vitamin synonyms
        question_lower = question.lower()
        question_words = [word for word in question_lower.split() if len(word) > 2]

        # Expand search terms with vitamin synonyms
        expanded_search_terms = self._expand_vitamin_synonyms(question_words)

        relevant_chunks = []
        chunk_indices_with_scores = []

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            chunk_lower = chunk.lower()

            # Score chunk based on keyword matches (including synonyms)
            score = 0
            for word in expanded_search_terms:
                if word in chunk_lower:
                    score += chunk_lower.count(word)

            if score > 0:
                chunk_indices_with_scores.append((i, score, chunk))

        # Sort by score (best matches first)
        chunk_indices_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Expand context window around best matches
        context_chunks_before = self.config.get('Search', 'context_chunks_before', fallback='2')
        context_chunks_after = self.config.get('Search', 'context_chunks_after', fallback='3')

        try:
            chunks_before = int(context_chunks_before)
            chunks_after = int(context_chunks_after)
        except ValueError:
            chunks_before, chunks_after = 2, 3  # Default fallback

        expanded_indices = set()

        # Expand context for each relevant chunk
        for chunk_idx, score, chunk in chunk_indices_with_scores[:5]:  # Top 5 matches
            # Add context window around this chunk
            start_idx = max(0, chunk_idx - chunks_before)
            end_idx = min(len(chunks), chunk_idx + chunks_after + 1)

            for idx in range(start_idx, end_idx):
                expanded_indices.add(idx)

        # Collect expanded chunks in order
        expanded_chunks = []
        for idx in sorted(expanded_indices):
            if chunks[idx].strip():
                chunk = chunks[idx]
                # Extract meaningful content (skip the factual relationships header)
                lines = chunk.split('\n')
                content_lines = []
                skip_header = True

                for line in lines:
                    if skip_header and ('FACTUAL RELATIONSHIPS:' in line or line.strip() == ''):
                        continue
                    skip_header = False

                    if line.strip() and not line.startswith('Extracted from'):
                        content_lines.append(line.strip())

                if content_lines:
                    chunk_content = ' '.join(content_lines[:15])  # More lines due to context expansion
                    expanded_chunks.append(chunk_content[:400])  # Longer chunks due to context

        # Log context expansion details
        total_context_chunks = len(expanded_chunks)
        original_matches = len(chunk_indices_with_scores)

        logger.debug("Context window expansion applied", {
            "original_matches": original_matches,
            "context_before": chunks_before,
            "context_after": chunks_after,
            "total_context_chunks": total_context_chunks
        })

        return expanded_chunks[:10]  # Return more chunks due to context expansion

    def _expand_vitamin_synonyms(self, search_terms: list[str]) -> list[str]:
        """Expand search terms with vitamin synonyms and common names."""
        expanded_terms = search_terms.copy()

        # Vitamin synonym mappings
        vitamin_synonyms = {
            'vitamin': ['vitamine', 'vitamins'],
            'b3': ['vitamin_b3', 'niacin', 'nikotinamid', 'nicotinamid', 'nicotinsäure'],
            'b1': ['vitamin_b1', 'thiamin', 'thiamine'],
            'b6': ['vitamin_b6', 'pyridoxin', 'pyridoxine'],
            'b12': ['vitamin_b12', 'cobalamin', 'cyanocobalamin'],
            'folsäure': ['folate', 'folacin', 'vitamin_b9', 'b9'],
            'magnesium': ['mg', 'magnesium_kalzium', 'drei_wichtige_mineralien'],
            'kalzium': ['calcium', 'ca', 'magnesium_kalzium'],
            'vitamin_d': ['d3', 'cholecalciferol', 'vitamin_d3']
        }

        # Expand terms based on synonyms
        for term in search_terms:
            term_lower = term.lower()
            for key, synonyms in vitamin_synonyms.items():
                if key in term_lower or term_lower in synonyms:
                    expanded_terms.extend(synonyms)
                    if key not in expanded_terms:
                        expanded_terms.append(key)

        # Remove duplicates and return
        return list(set(expanded_terms))

    def _handle_general_knowledge_question(self, question: str) -> str:
        """
        Handle pure general knowledge questions using Claude without document context.

        Args:
            question: General knowledge question

        Returns:
            Direct answer from Claude
        """
        if not self.llm_client.client:
            return ("Entschuldigung, der Analysedienst ist momentan nicht verfügbar. "
                   "Bitte überprüfe die API-Konfiguration.")

        try:
            logger.performance_start("general_qa")

            # Simple direct prompt for general knowledge
            general_prompt = f"""Du bist ein hilfreicher Assistent. Beantworte die folgende Frage direkt und präzise:

Frage: {question}

Antwort:"""

            # Call Claude API directly for general knowledge
            response = self.llm_client.client.messages.create(
                model=self.llm_client.settings.llm_model,
                max_tokens=500,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": general_prompt
                }]
            )

            answer = response.content[0].text.strip()

            logger.performance_end("general_qa")
            logger.info("General knowledge Q&A completed", {
                "question_length": len(question),
                "answer_length": len(answer),
                "processing_type": "general_knowledge"
            })

            return answer

        except Exception as e:
            logger.error("General knowledge Q&A failed", e)
            return "Entschuldigung, ich konnte deine Frage nicht bearbeiten. Bitte versuche es erneut."

# NOTE: Old categorization methods removed - now using QuestionRouter class
# See QuestionRouter in utils/question_router.py for the new implementation

    def _search_with_keywords(self, question: str) -> tuple[list[str], str]:
        """Fallback keyword-based search in current document chunks."""
        logger.debug("Using keyword-based search fallback")

        relevant_chunks = []
        question_lower = question.lower()

        # Simple keyword matching in neutralized content
        for chunk in self.last_processed_data.chunks[:50]:  # Search in first 50 chunks
            if chunk.neutralized_content:
                content_lower = chunk.neutralized_content.lower()
                # Check if any word from question appears in chunk
                question_words = question_lower.split()
                if any(word in content_lower for word in question_words if len(word) > 3):
                    relevant_chunks.append(chunk.neutralized_content[:300])

        return relevant_chunks, "keyword_search"

    def _persist_qa_exchange(self, question: str, answer: str, context: str, search_method: str):
        """Persist Q&A exchange to database for future semantic search."""
        try:
            from .persistence.repository import SessionRepository
            from datetime import datetime
            from sqlalchemy import desc

            repo = SessionRepository(self.db_manager.get_session())

            logger.database_operation("Persisting Q&A exchange", {
                "question_length": len(question),
                "answer_length": len(answer),
                "search_method": search_method,
                "context_length": len(context)
            })

            # Find the most recent session (from latest document analysis)
            from .persistence.models import PersistentQASession
            session = repo._get_session()
            latest_qa_session = session.query(PersistentQASession).order_by(desc(PersistentQASession.created_at)).first()

            if latest_qa_session:
                # Add Q&A exchange to the latest session
                # Map search method to valid answer_origin values
                answer_origin_mapping = {
                    "session_content_search": "neutralized",
                    "fts5_semantic_search": "synthesized",
                    "keyword_search": "neutralized",
                    "no_results": "synthesized"
                }
                answer_origin = answer_origin_mapping.get(search_method, "neutralized")

                exchange = repo.add_qa_exchange(
                    session_id=latest_qa_session.session_id,
                    question=question,
                    answer=answer,
                    context_used=context,
                    answer_origin=answer_origin,
                    confidence_score=0.8,  # Default confidence
                    processing_time=0.5,   # Estimated processing time
                    tokens_used=len(question.split()) + len(answer.split()),  # Rough token estimate
                    claude_model="claude-sonnet-4-20250514"
                )

                if exchange:
                    logger.info("Q&A exchange persisted successfully", {
                        "exchange_id": exchange.exchange_id,
                        "session_id": latest_qa_session.session_id
                    })
                else:
                    logger.warning("Failed to persist Q&A exchange - add_qa_exchange returned None")
            else:
                logger.warning("No active session found - Q&A exchange not persisted")

        except Exception as e:
            logger.error("Failed to persist Q&A exchange", e)
            raise

    def get_analysis_report(self) -> Optional["AnalysisReport"]:
        """
        Get comprehensive analysis report for UI display.

        Returns:
            AnalysisReport with full statistics and transparency data,
            or None if no analysis has been performed yet.
        """
        if not hasattr(self, 'last_analysis_statistics') or not self.last_analysis_statistics:
            logger.warning("No analysis statistics available - document must be analyzed first")
            return None

        try:
            from .models.analysis_statistics import AnalysisReport

            # Create comprehensive analysis report
            report = AnalysisReport(
                statistics=self.last_analysis_statistics
            )

            logger.debug("Analysis report generated successfully", {
                "document_name": report.statistics.document_name,
                "total_entities": report.statistics.merge_analysis.total_entities_after_merge,
                "transmission_safe": report.statistics.compliance_report.transmission_safe,
                "processing_time": f"{report.statistics.performance.total_processing_seconds:.2f}s"
            })

            return report

        except Exception as e:
            logger.error("Failed to generate analysis report", e)
            return None

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