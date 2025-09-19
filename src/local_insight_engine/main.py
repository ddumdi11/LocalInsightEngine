"""
Main entry point for LocalInsightEngine application.
"""

import logging
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

        # Store processed data for Q&A (legacy fallback)
        self.last_processed_data = None
        self.last_analysis_result = None

        # Test dependencies
        logger.test_dependencies()

        logger.info("LocalInsightEngine initialized successfully")
    
    def analyze_document(self, document_path: Path, factual_mode: bool = False) -> dict:
        """
        Analyze a document through the 3-layer architecture.

        Args:
            document_path: Path to the document to analyze
            factual_mode: If True, disables anonymization of common factual terms

        Returns:
            Analysis results dictionary
        """
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

            # TODO: Fix persistence models and re-enable analysis persistence
            # if self.db_manager:
            #     try:
            #         self._persist_analysis(document_path, processed_data, analysis, factual_mode)
            #     except Exception as e:
            #         logger.error("Failed to persist analysis to database", e)

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
            neutralized_context = (
                processed_data.chunks[0].neutralized_content if processed_data.chunks else ""
            )
            created = repo.create_session(
                document_path=str(document_path),
                analysis_result=analysis,
                neutralized_context=neutralized_context,
                factual_mode=factual_mode,
                chunk_count=len(processed_data.chunks),
                entity_count=len(getattr(processed_data, "all_entities", [])),
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
            Answer based on neutralized document content
        """
        logger.performance_start("qa_session")
        logger.step("Processing Q&A question", {"question": question})

        if not self.last_processed_data:
            logger.warning("No document data available for Q&A")
            return "No document has been analyzed yet. Please analyze a document first."

        try:
            # Enhanced search: Try FTS5 if database is available, fallback to keyword matching
            relevant_chunks = []
            search_method = "unknown"

            if self.db_manager:
                try:
                    relevant_chunks, search_method = self._search_with_fts5(question)
                except Exception as e:
                    logger.warning("FTS5 search failed, falling back to keyword matching", e)
                    relevant_chunks, search_method = self._search_with_keywords(question)
            else:
                relevant_chunks, search_method = self._search_with_keywords(question)

            logger.debug("Search completed", {
                "method": search_method,
                "chunks_found": len(relevant_chunks),
                "question": question
            })

            # If no relevant chunks found, use first few chunks as context
            if not relevant_chunks:
                relevant_chunks = [
                    chunk.neutralized_content[:300]
                    for chunk in self.last_processed_data.chunks[:10]
                    if chunk.neutralized_content
                ]
                search_method = "fallback_first_chunks"
                logger.debug("Using fallback chunks", {"chunk_count": len(relevant_chunks)})

            # Create context from relevant chunks
            context = "\n".join(relevant_chunks[:5])  # Max 5 chunks

            # Create Q&A prompt
            from .models.text_data import ProcessedText, TextChunk

            qa_context = f"""

Based on the following document content, please answer the user's question.

Document content:
{context}

Question: {question}

Please provide a helpful and accurate answer based only on the document content provided.
"""

            # Create ProcessedText for Q&A
            qa_processed = ProcessedText(
                id=uuid4(),
                source_document_id=self.last_processed_data.source_document_id,
                chunks=[
                    TextChunk(
                        id=uuid4(),
                        neutralized_content=qa_context,
                        source_document_id=self.last_processed_data.source_document_id,
                        original_char_range=(0, len(qa_context)),
                        word_count=len(qa_context.split())
                    )
                ]
            )

            # Use dedicated Q&A method for better results
            logger.performance_start("llm_qa")
            try:
                # Try the new specialized Q&A method first
                if hasattr(self.llm_client, 'answer_question'):
                    answer = self.llm_client.answer_question(self.last_processed_data, question)
                else:
                    # Fallback to general analysis method
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
        formats: Optional[list] = None
    ) -> dict:
        """
        Analyze a document and export results in specified formats.
        
        Args:
            document_path: Path to the document to analyze
            output_path: Path for export files (without extension)
            formats: List of export formats (default: ["json"])
            
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
            analysis, processed_data, document, output_path, formats
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
            analysis_result, processed_text, document, output_path, formats
        )

    def _search_with_fts5(self, question: str) -> tuple[list[str], str]:
        """Search using FTS5 semantic search in database."""
        try:
            from .persistence.repository import SessionRepository

            repo = SessionRepository(self.db_manager.get_session())
            search_results = repo.search_qa_content(
                query=question,
                limit=10,
                time_decay_weight=0.2,  # Less emphasis on recency for current document
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
                # No FTS5 results, fall back to current document chunks
                return [], "fts5_no_results"

        except Exception as e:
            logger.error("FTS5 search failed", e)
            raise

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

            repo = SessionRepository(self.db_manager.get_session())

            # Try to find existing session for current document
            # For now, create a simple session if none exists
            # TODO: Improve this to properly link with document analysis sessions

            logger.database_operation("Persisting Q&A exchange", {
                "question_length": len(question),
                "answer_length": len(answer),
                "search_method": search_method,
                "context_length": len(context)
            })

            # For now, we'll add this as a simple Q&A exchange
            # In a full implementation, we'd link this to the proper session
            logger.info("Q&A exchange logged for future semantic search")

        except Exception as e:
            logger.error("Failed to persist Q&A exchange", e)
            raise

    def get_analysis_report(self):
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