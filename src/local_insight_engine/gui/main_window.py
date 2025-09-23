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
from .analysis_report_window import AnalysisReportWindow

logger = logging.getLogger(__name__)


class LocalInsightEngineGUI:
    def __init__(self, root=None):
        # Use provided root or create new one
        self.root = root if root is not None else tk.Tk()
        self.root.title(f"LocalInsightEngine {__version__} - GUI")
        self.root.geometry("900x700")

        self.engine = LocalInsightEngine()
        self.current_document: Optional[Path] = None
        self.analysis_result: Optional[AnalysisResult] = None

        # Load context defaults after engine is initialized
        self.load_context_defaults()

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

        # Factual content mode checkbox
        self.factual_mode_var = tk.BooleanVar(value=False)
        self.factual_checkbox = ttk.Checkbutton(
            actions_frame,
            text="Sachbuch-Modus (keine Anonymisierung gängiger Begriffe)",
            variable=self.factual_mode_var
        )
        self.factual_checkbox.grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

        # Re-analyze button (initially hidden)
        self.reanalyze_button = ttk.Button(
            actions_frame,
            text="🔄 Neu analysieren im Standard-Modus",
            command=self.reanalyze_other_mode
        )
        # Initially hide the button
        self.reanalyze_button.grid_remove()

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

        # Analysis report button (initially hidden)
        self.analysis_report_button = ttk.Button(
            actions_frame,
            text="📊 Analyseprotokoll aufrufen",
            command=self.show_analysis_report
        )
        # Initially hide the button
        self.analysis_report_button.grid_remove()

    def setup_qa_section(self, parent):
        """Setup Q&A section"""
        # Context window configuration frame
        context_frame = ttk.LabelFrame(parent, text="Context Window Settings", padding="5")
        context_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        context_frame.columnconfigure(2, weight=1)

        # Context before setting
        ttk.Label(context_frame, text="Context before hit:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.context_before_var = tk.IntVar(value=2)
        self.context_before_spinbox = ttk.Spinbox(
            context_frame,
            from_=0,
            to=10,
            width=5,
            textvariable=self.context_before_var,
            command=self.on_context_change
        )
        self.context_before_spinbox.grid(row=0, column=1, padx=(0, 15))

        # Context after setting
        ttk.Label(context_frame, text="Context after hit:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.context_after_var = tk.IntVar(value=3)
        self.context_after_spinbox = ttk.Spinbox(
            context_frame,
            from_=0,
            to=10,
            width=5,
            textvariable=self.context_after_var,
            command=self.on_context_change
        )
        self.context_after_spinbox.grid(row=0, column=3, padx=(0, 15))

        # Save as default button
        ttk.Button(context_frame, text="Save as Default", command=self.save_context_defaults).grid(
            row=0, column=4, padx=(5, 0)
        )

        # Q&A section
        qa_frame = ttk.LabelFrame(parent, text="Q&A - Ask questions about your document", padding="5")
        qa_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
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
            # Get factual mode setting from GUI
            factual_mode = self.factual_mode_var.get()
            analysis_dict = self.engine.analyze_document(self.current_document, factual_mode=factual_mode)
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

        # Show analysis report button (use row=3 to avoid overlap with re-analyze button)
        self.analysis_report_button.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))

        # Update factual mode UI after analysis
        self._update_factual_mode_ui()

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
            # Update engine config with current GUI context settings
            if hasattr(self.engine, 'config'):
                # Ensure Search section exists
                if not self.engine.config.has_section('Search'):
                    self.engine.config.add_section('Search')

                # Update with current GUI values
                self.engine.config.set('Search', 'context_chunks_before', str(self.context_before_var.get()))
                self.engine.config.set('Search', 'context_chunks_after', str(self.context_after_var.get()))

            # Use the engine's new answer_question method that searches through original chunks
            answer = self.engine.answer_question(question)

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

    def _update_factual_mode_ui(self):
        """Update factual mode UI after analysis"""
        if self.analysis_result:
            # Disable checkbox and update text
            current_mode = self.factual_mode_var.get()
            if current_mode:
                self.factual_checkbox.config(
                    state="disabled",
                    text="☑ Sachbuch-Modus aktiv"
                )
                self.reanalyze_button.config(text="🔄 Neu analysieren im Standard-Modus")
            else:
                self.factual_checkbox.config(
                    state="disabled",
                    text="☐ Standard-Modus aktiv"
                )
                self.reanalyze_button.config(text="🔄 Neu analysieren im Sachbuch-Modus")

            # Show re-analyze button
            self.reanalyze_button.grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        else:
            # Enable checkbox for new analysis
            self.factual_checkbox.config(
                state="normal",
                text="Sachbuch-Modus (keine Anonymisierung gängiger Begriffe)"
            )
            # Hide re-analyze button
            self.reanalyze_button.grid_remove()

    def reanalyze_other_mode(self):
        """Re-analyze document in the other mode"""
        if not self.current_document:
            messagebox.showwarning("No Document", "Please select a document first.")
            return

        # Toggle the mode
        current_mode = self.factual_mode_var.get()
        self.factual_mode_var.set(not current_mode)

        # Reset UI to pre-analysis state temporarily
        self.factual_checkbox.config(state="normal")
        self.reanalyze_button.grid_remove()

        # Log the mode switch
        new_mode = "Sachbuch-Modus" if not current_mode else "Standard-Modus"
        self.log_message(f"🔄 Wechsle zu {new_mode} und analysiere neu...")

        # Start re-analysis
        self.run_in_thread(self._analyze_document_bg)

    def show_analysis_report(self):
        """Show the comprehensive analysis report window"""
        try:
            # Get analysis report from engine
            report = self.engine.get_analysis_report()

            if not report:
                messagebox.showwarning(
                    "No Analysis Data",
                    "No analysis statistics available. Please analyze a document first."
                )
                return

            # Create and show analysis report window
            AnalysisReportWindow(self.root, report)

        except Exception as e:
            self.log_message(f"✗ Failed to open analysis report: {e}")
            messagebox.showerror("Report Error", f"Failed to open analysis report:\n{e}")

    def on_context_change(self):
        """Handle context window setting changes"""
        before = self.context_before_var.get()
        after = self.context_after_var.get()
        self.log_message(f"Context window updated: {before} before, {after} after hit")

    def save_context_defaults(self):
        """Save current context settings as defaults to config file"""
        try:
            import configparser
            from pathlib import Path

            config_path = Path("localinsightengine.conf")
            config = configparser.ConfigParser()

            # Read existing config
            if config_path.exists():
                config.read(config_path, encoding='utf-8')

            # Ensure Search section exists
            if not config.has_section('Search'):
                config.add_section('Search')

            # Update values
            config.set('Search', 'context_chunks_before', str(self.context_before_var.get()))
            config.set('Search', 'context_chunks_after', str(self.context_after_var.get()))

            # Write back to file
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

            before = self.context_before_var.get()
            after = self.context_after_var.get()
            self.log_message(f"✓ Context defaults saved: {before} before, {after} after hit")
            messagebox.showinfo("Settings Saved", f"Context window defaults saved:\n{before} chunks before, {after} chunks after hit")

        except Exception as e:
            self.log_message(f"✗ Failed to save context defaults: {e}")
            messagebox.showerror("Save Error", f"Failed to save context defaults:\n{e}")

    def load_context_defaults(self):
        """Load context settings from config file"""
        try:
            if hasattr(self, 'engine') and self.engine:
                before = int(self.engine.config.get('Search', 'context_chunks_before', fallback='2'))
                after = int(self.engine.config.get('Search', 'context_chunks_after', fallback='3'))

                self.context_before_var.set(before)
                self.context_after_var.set(after)
                self.log_message(f"Context defaults loaded: {before} before, {after} after hit")
        except Exception as e:
            self.log_message(f"Could not load context defaults: {e}")

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