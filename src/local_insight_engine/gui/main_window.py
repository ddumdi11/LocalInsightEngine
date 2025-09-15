"""
Main GUI window for LocalInsightEngine
Provides file selection, analysis actions, and Q&A functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from local_insight_engine.main import LocalInsightEngine
from local_insight_engine.models.analysis import AnalysisResult
from local_insight_engine import __version__

logger = logging.getLogger(__name__)


class LocalInsightEngineGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"LocalInsightEngine {__version__} - GUI")
        self.root.geometry("900x700")

        self.engine = LocalInsightEngine()
        self.current_document: Optional[Path] = None
        self.analysis_result: Optional[AnalysisResult] = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # File selection section
        self.setup_file_section(main_frame)

        # Action buttons section
        self.setup_actions_section(main_frame)

        # Q&A section
        self.setup_qa_section(main_frame)

        # Status/Log section
        self.setup_status_section(main_frame)

    def setup_file_section(self, parent):
        """Setup file selection section"""
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="Document Selection", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # File path entry
        ttk.Label(file_frame, text="Document:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        # Browse button
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2)

        # File info label
        self.file_info_var = tk.StringVar(value="No document selected")
        ttk.Label(file_frame, textvariable=self.file_info_var, foreground="gray").grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0)
        )

    def setup_actions_section(self, parent):
        """Setup action buttons section"""
        actions_frame = ttk.LabelFrame(parent, text="Analysis Actions", padding="5")
        actions_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Button frame for better layout
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Action buttons
        ttk.Button(btn_frame, text="Analyze Document", command=self.analyze_document).grid(
            row=0, column=0, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="Analyze & Export", command=self.analyze_and_export).grid(
            row=0, column=1, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="Run Tests", command=self.run_tests).grid(
            row=0, column=2, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="Show Version", command=self.show_version).grid(
            row=0, column=3
        )

    def setup_qa_section(self, parent):
        """Setup Q&A section"""
        qa_frame = ttk.LabelFrame(parent, text="Q&A - Ask questions about your document", padding="5")
        qa_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        qa_frame.columnconfigure(0, weight=1)
        qa_frame.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

        # Question input frame
        question_frame = ttk.Frame(qa_frame)
        question_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        question_frame.columnconfigure(0, weight=1)

        # Question entry
        ttk.Label(question_frame, text="Your Question:").grid(row=0, column=0, sticky=tk.W)
        self.question_var = tk.StringVar()
        self.question_entry = ttk.Entry(question_frame, textvariable=self.question_var)
        self.question_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.question_entry.bind("<Return>", lambda e: self.ask_question())

        # Ask button
        self.ask_button = ttk.Button(question_frame, text="Ask", command=self.ask_question, state="disabled")
        self.ask_button.grid(row=1, column=1)

        # Answer area
        ttk.Label(qa_frame, text="Answer:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.answer_text = scrolledtext.ScrolledText(qa_frame, height=10, wrap=tk.WORD, state="disabled")
        self.answer_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_status_section(self, parent):
        """Setup status/log section"""
        status_frame = ttk.LabelFrame(parent, text="Status & Log", padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        # Status text area
        self.status_text = scrolledtext.ScrolledText(status_frame, height=6, wrap=tk.WORD, state="disabled")
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Clear log button
        ttk.Button(status_frame, text="Clear Log", command=self.clear_log).grid(
            row=1, column=0, sticky=tk.E, pady=(5, 0)
        )

    def browse_file(self):
        """Open file dialog to select document"""
        filetypes = [
            ("All supported", "*.pdf;*.txt;*.epub;*.docx"),
            ("PDF files", "*.pdf"),
            ("Text files", "*.txt"),
            ("EPUB files", "*.epub"),
            ("Word documents", "*.docx"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Document to Analyze",
            filetypes=filetypes
        )

        if filename:
            self.current_document = Path(filename)
            self.file_path_var.set(str(self.current_document))
            self.file_info_var.set(f"Selected: {self.current_document.name} ({self.get_file_size_str()})")
            self.ask_button.config(state="normal")
            self.log_message(f"Document selected: {self.current_document}")

    def get_file_size_str(self) -> str:
        """Get human-readable file size"""
        if not self.current_document or not self.current_document.exists():
            return "unknown size"

        size = self.current_document.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def log_message(self, message: str):
        """Add message to status log"""
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def clear_log(self):
        """Clear the status log"""
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")

    def run_in_thread(self, func):
        """Run function in background thread"""
        thread = threading.Thread(target=func, daemon=True)
        thread.start()

    def analyze_document(self):
        """Analyze the selected document"""
        if not self.current_document:
            messagebox.showwarning("No Document", "Please select a document first.")
            return

        self.log_message("Starting document analysis...")
        self.run_in_thread(self._analyze_document_bg)

    def _analyze_document_bg(self):
        """Background thread for document analysis"""
        try:
            analysis_dict = self.engine.analyze_document(self.current_document)
            # Convert dict to AnalysisResult object with robust error handling
            if isinstance(analysis_dict, dict):
                try:
                    self.analysis_result = AnalysisResult.parse_obj(analysis_dict)
                except Exception as parse_error:
                    logger.warning(f"Failed to parse analysis result as AnalysisResult: {parse_error}")
                    # Fallback: keep as dict for Q&A functionality
                    self.analysis_result = analysis_dict
            else:
                self.analysis_result = analysis_dict
            self.root.after(0, self._analysis_complete)
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._analysis_error(msg))

    def _analysis_complete(self):
        """Handle successful analysis completion"""
        self.log_message("✓ Analysis completed successfully!")
        self.ask_button.config(state="normal")

    def _analysis_error(self, error_msg: str):
        """Handle analysis error"""
        self.log_message(f"✗ Analysis failed: {error_msg}")
        messagebox.showerror("Analysis Error", f"Analysis failed:\n{error_msg}")

    def analyze_and_export(self):
        """Analyze and export document"""
        if not self.current_document:
            messagebox.showwarning("No Document", "Please select a document first.")
            return

        # Ask for export location
        export_path = filedialog.asksaveasfilename(
            title="Save Analysis Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not export_path:
            return

        self.log_message(f"Starting analysis and export to: {Path(export_path).name}")
        self.run_in_thread(lambda: self._analyze_and_export_bg(export_path))

    def _analyze_and_export_bg(self, export_path: str):
        """Background thread for analyze and export"""
        try:
            # Run CLI command with export (using same Python interpreter)
            result = subprocess.run([
                sys.executable, "-m", "local_insight_engine.main",
                str(self.current_document),
                "--export",
                "--output", str(Path(export_path).parent)
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)

            if result.returncode == 0:
                self.root.after(0, lambda: self.log_message(f"✓ Analysis and export completed: {export_path}"))
            else:
                self.root.after(0, lambda: self._analysis_error(result.stderr or "Unknown error"))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._analysis_error(msg))

    def ask_question(self):
        """Ask question about the analyzed document"""
        question = self.question_var.get().strip()
        if not question:
            return

        if not self.analysis_result:
            messagebox.showwarning("No Analysis", "Please analyze a document first before asking questions.")
            return

        self.log_message(f"Question: {question}")
        self.answer_text.config(state="normal")
        self.answer_text.insert(tk.END, f"\n🙋 Question: {question}\n")
        self.answer_text.insert(tk.END, "🤔 Thinking...\n")
        self.answer_text.see(tk.END)
        self.answer_text.config(state="disabled")

        self.question_var.set("")
        self.ask_button.config(state="disabled")

        self.run_in_thread(lambda: self._ask_question_bg(question))

    def _ask_question_bg(self, question: str):
        """Background thread for Q&A"""
        try:
            # Use the analysis engine to answer questions about the neutralized content
            from local_insight_engine.services.analysis_engine.claude_client import ClaudeClient

            analyzer = ClaudeClient()

            # Get neutralized content from analysis result (works with both AnalysisResult objects and dicts)
            neutralized_content = ""
            if self.analysis_result:
                # Handle AnalysisResult object
                if hasattr(self.analysis_result, 'executive_summary'):
                    if self.analysis_result.executive_summary:
                        neutralized_content = self.analysis_result.executive_summary
                    elif hasattr(self.analysis_result, 'main_themes') and self.analysis_result.main_themes:
                        neutralized_content = "Main themes: " + ", ".join(self.analysis_result.main_themes)
                    elif hasattr(self.analysis_result, 'insights') and self.analysis_result.insights:
                        neutralized_content = "\n".join([insight.content for insight in self.analysis_result.insights])
                # Handle dict
                elif isinstance(self.analysis_result, dict):
                    if 'executive_summary' in self.analysis_result and self.analysis_result['executive_summary']:
                        neutralized_content = self.analysis_result['executive_summary']
                    elif 'main_themes' in self.analysis_result and self.analysis_result['main_themes']:
                        neutralized_content = "Main themes: " + ", ".join(self.analysis_result['main_themes'])
                    elif 'insights' in self.analysis_result and self.analysis_result['insights']:
                        insights = self.analysis_result['insights']
                        if isinstance(insights, list):
                            neutralized_content = "\n".join([str(insight) for insight in insights])
                        else:
                            neutralized_content = str(insights)
                    else:
                        # Fallback: use any available content from the dict
                        neutralized_content = str(self.analysis_result)[:1000]

                if not neutralized_content:
                    neutralized_content = "Analysis result available but no suitable content found for Q&A."

            # Create context for the question
            context = f"""
            Based on the following analyzed content, please answer the user's question.

            Content: {neutralized_content[:3000]}...

            Question: {question}

            Please provide a helpful answer based only on the content provided.
            """

            # Get answer from Claude
            # Create a simple ProcessedText-like object for the question
            from local_insight_engine.models.text_data import ProcessedText, TextChunk
            from uuid import uuid4

            # Create a minimal ProcessedText object with the question context
            processed_text = ProcessedText(
                id=uuid4(),
                source_document_id=uuid4(),
                chunks=[
                    TextChunk(
                        id=uuid4(),
                        neutralized_content=context,
                        source_document_id=uuid4(),
                        original_char_range=(0, len(context)),
                        word_count=len(context.split())
                    )
                ]
            )

            result = analyzer.analyze(processed_text)

            # Debug: Log what we get back from Claude
            print(f"DEBUG: Claude result type: {type(result)}")
            print(f"DEBUG: Claude result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            print(f"DEBUG: Claude result: {result}")

            # Try different ways to extract the answer
            answer = None
            if isinstance(result, dict):
                # Try various possible keys
                answer = (result.get('summary') or
                         result.get('answer') or
                         result.get('response') or
                         result.get('content') or
                         result.get('text') or
                         str(result))
            else:
                answer = str(result)

            if not answer or answer == 'None':
                answer = 'Sorry, I could not extract an answer from the analysis result.'

            self.root.after(0, lambda: self._question_answered(answer))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._question_error(msg))

    def _question_answered(self, answer: str):
        """Handle successful question answering"""
        self.answer_text.config(state="normal")
        # Remove "Thinking..." line
        self.answer_text.delete("end-2l", "end-1l")
        self.answer_text.insert(tk.END, f"💡 Answer: {answer}\n")
        self.answer_text.see(tk.END)
        self.answer_text.config(state="disabled")

        self.ask_button.config(state="normal")
        self.log_message("✓ Question answered")

    def _question_error(self, error_msg: str):
        """Handle question answering error"""
        self.answer_text.config(state="normal")
        # Remove "Thinking..." line
        self.answer_text.delete("end-2l", "end-1l")
        self.answer_text.insert(tk.END, f"❌ Error: {error_msg}\n")
        self.answer_text.see(tk.END)
        self.answer_text.config(state="disabled")

        self.ask_button.config(state="normal")
        self.log_message(f"✗ Question error: {error_msg}")

    def run_tests(self):
        """Run test suite"""
        self.log_message("Running test suite...")
        self.run_in_thread(self._run_tests_bg)

    def _run_tests_bg(self):
        """Background thread for running tests"""
        try:
            result = subprocess.run([
                sys.executable, "tests/test_multiformat.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)

            if result.returncode == 0:
                self.root.after(0, lambda: self.log_message("✓ Tests completed successfully"))
            else:
                self.root.after(0, lambda: self.log_message(f"✗ Tests failed: {result.stderr}"))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.log_message(f"✗ Test error: {msg}"))

    def show_version(self):
        """Show version information"""
        version_info = f"""LocalInsightEngine {__version__}

Copyright-compliant document analysis with 3-layer architecture:
• Layer 1: Document parsing (PDF, TXT, EPUB, DOCX)
• Layer 2: Text processing & neutralization
• Layer 3: LLM-based analysis

GUI Features:
• File selection and analysis
• Export to JSON
• Interactive Q&A about documents
• Test suite execution"""

        messagebox.showinfo("Version Information", version_info)
        self.log_message("Version information displayed")

    def run(self):
        """Start the GUI application"""
        self.log_message("LocalInsightEngine GUI started")
        self.log_message("Select a document and click 'Analyze Document' to begin")
        self.root.mainloop()


def main():
    """Entry point for GUI application"""
    app = LocalInsightEngineGUI()
    app.run()


if __name__ == "__main__":
    main()