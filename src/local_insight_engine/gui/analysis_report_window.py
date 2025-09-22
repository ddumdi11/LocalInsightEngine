"""
Analysis Report Window for LocalInsightEngine
Displays comprehensive analysis statistics with local transparency and transmission preview
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class AnalysisReportWindow:
    def __init__(self, parent, analysis_report):
        """
        Initialize the analysis report window.

        Args:
            parent: Parent window
            analysis_report: AnalysisReport object with comprehensive statistics
        """
        self.parent = parent
        self.report = analysis_report

        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Analyseprotokoll - LocalInsightEngine")
        self.window.geometry("1000x800")
        self.window.transient(parent)
        self.window.grab_set()

        self.setup_ui()

        # Center window on parent
        self.center_window()

    def setup_ui(self) -> None:
        """Setup the report UI with tabs for different sections"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title section
        self.setup_title_section(main_frame)

        # Tabbed interface
        self.setup_tabs(main_frame)

        # Buttons section
        self.setup_buttons_section(main_frame)

    def setup_title_section(self, parent) -> None:
        """Setup title and summary section"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(title_frame, text="📊 Comprehensive Analysis Report",
                 font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # Document info
        stats = self.report.statistics
        ttk.Label(title_frame, text="Document:", font=("TkDefaultFont", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Label(title_frame, text=stats.document_name).grid(row=1, column=1, sticky=tk.W)

        # Summary stats
        summary = self.report.get_summary_stats()
        summary_text = (
            f"Processing: {summary['processing_time']} | "
            f"Chunks: {summary['chunks_created']} | "
            f"Entities: {summary['entities_total']} | "
            f"Mode: {'Factual' if summary['factual_mode'] else 'Standard'} | "
            f"Status: {'✅ Safe' if summary['transmission_safe'] else '❌ Risk'}"
        )
        ttk.Label(title_frame, text=summary_text, foreground="gray").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

    def setup_tabs(self, parent) -> None:
        """Setup tabbed interface for different report sections"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Tab 1: Local Transparency (shows original entities)
        self.setup_local_transparency_tab()

        # Tab 2: Transmission Preview (shows anonymized entities)
        self.setup_transmission_preview_tab()

        # Tab 3: Processing Statistics
        self.setup_processing_stats_tab()

        # Tab 4: Compliance Report
        self.setup_compliance_tab()

        # Tab 5: Semantic Triples (only in factual mode)
        self.setup_semantic_triples_tab()

    def setup_local_transparency_tab(self) -> None:
        """Setup local transparency tab showing original entities"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Local Transparency")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Header
        header = ttk.Label(frame, text="🔍 ORIGINAL ENTITIES FOUND IN YOUR DOCUMENT",
                          font=("TkDefaultFont", 12, "bold"))
        header.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        # Get local transparency data
        local_data = self.report.get_local_transparency_section()

        if "error" in local_data:
            ttk.Label(frame, text=local_data["error"]).grid(row=1, column=0, padx=10, pady=10)
            return

        # Create scrollable text area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Format and display local transparency data
        content = self._format_local_transparency_data(local_data)
        text_area.insert(tk.END, content)
        text_area.config(state="disabled")

    def setup_transmission_preview_tab(self) -> None:
        """Setup transmission preview tab showing anonymized entities"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📡 Transmission Preview")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Header
        header = ttk.Label(frame, text="📡 WHAT WOULD BE SENT TO EXTERNAL APIS",
                          font=("TkDefaultFont", 12, "bold"))
        header.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        # Get transmission preview data
        transmission_data = self.report.get_transmission_preview_section()

        if "error" in transmission_data:
            ttk.Label(frame, text=transmission_data["error"]).grid(row=1, column=0, padx=10, pady=10)
            return

        # Create scrollable text area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Format and display transmission preview data
        content = self._format_transmission_preview_data(transmission_data)
        text_area.insert(tk.END, content)
        text_area.config(state="disabled")

    def setup_processing_stats_tab(self) -> None:
        """Setup processing statistics tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⏱️ Processing Stats")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Create scrollable text area
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 9))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Format and display processing statistics
        content = self._format_processing_stats()
        text_area.insert(tk.END, content)
        text_area.config(state="disabled")

    def setup_compliance_tab(self) -> None:
        """Setup compliance report tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚖️ Compliance")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Create scrollable text area
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 9))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Format and display compliance report
        content = self._format_compliance_report()
        text_area.insert(tk.END, content)
        text_area.config(state="disabled")

    def setup_buttons_section(self, parent) -> None:
        """Setup buttons for export and close"""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, sticky=tk.E)

        ttk.Button(btn_frame, text="📄 Export as PDF", command=self.export_pdf).grid(
            row=0, column=0, padx=(0, 5))
        ttk.Button(btn_frame, text="📝 Export as Markdown", command=self.export_markdown).grid(
            row=0, column=1, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 Export as JSON", command=self.export_json).grid(
            row=0, column=2, padx=(0, 15))
        ttk.Button(btn_frame, text="Close", command=self.window.destroy).grid(
            row=0, column=3)

    def _format_local_transparency_data(self, data: Dict[str, Any]) -> str:
        """Format local transparency data for display"""
        content = f"{data['title']}\n"
        content += "=" * len(data['title']) + "\n\n"
        content += f"Total entities found: {data['total_entities']}\n\n"

        for entity_type, info in data['entity_breakdown'].items():
            content += f"{entity_type} ({info['count']} found):\n"
            for example in info['examples']:
                content += f"  • {example}\n"
            content += "\n"

        content += f"\nNote: {data['note']}\n"
        content += "\nThis local view shows all entities exactly as they appear in your document.\n"
        content += "These original names are NEVER transmitted to external APIs.\n"

        return content

    def _format_transmission_preview_data(self, data: Dict[str, Any]) -> str:
        """Format transmission preview data for display"""
        content = f"{data['title']}\n"
        content += "=" * len(data['title']) + "\n\n"
        content += f"Compliance Status: {data['compliance_status']}\n"
        content += f"Total entities for transmission: {data['total_entities']}\n\n"

        if data['warnings']:
            content += "⚠️  WARNINGS:\n"
            for warning in data['warnings']:
                content += f"  • {warning}\n"
            content += "\n"

        for entity_type, info in data['entity_breakdown'].items():
            content += f"{entity_type} ({info['count']} entities):\n"
            for example in info['examples']:
                content += f"  • {example}\n"
            content += "\n"

        content += f"\nNote: {data['note']}\n"
        content += "\nThis preview shows exactly what would be sent to external APIs.\n"
        content += "All sensitive information has been anonymized for copyright compliance.\n"

        return content

    def _format_processing_stats(self) -> str:
        """Format processing statistics for display"""
        stats = self.report.statistics
        perf = stats.performance

        content = "PROCESSING PERFORMANCE STATISTICS\n"
        content += "=" * 35 + "\n\n"

        content += f"Document Information:\n"
        content += f"  • Name: {stats.document_name}\n"
        content += f"  • Size: {stats.document_size_bytes:,} bytes\n"
        content += f"  • Format: {stats.document_format}\n"
        content += f"  • Text Length: {stats.total_text_length:,} characters\n\n"

        content += f"Chunk Processing:\n"
        content += f"  • Chunks Created: {stats.chunks_created}\n"
        content += f"  • Chunk Size Range: {stats.chunk_size_range[0]}-{stats.chunk_size_range[1]} chars\n"
        content += f"  • Average Chunk Size: {stats.average_chunk_size:.0f} chars\n\n"

        content += f"Processing Times:\n"
        content += f"  • Document Loading: {perf.document_loading_seconds:.3f}s\n"
        content += f"  • Text Processing: {perf.text_processing_seconds:.3f}s\n"
        content += f"  • Entity Extraction: {perf.entity_extraction_total_seconds:.3f}s\n"
        content += f"  • LLM Analysis: {perf.llm_analysis_seconds:.3f}s\n"
        content += f"  • Total Processing: {perf.total_processing_seconds:.3f}s\n\n"

        content += f"Entity Extraction Stages:\n"
        for stage in stats.extraction_stages:
            content += f"  • {stage.stage_name} ({stage.process_name}):\n"
            content += f"    - Entities: {stage.total_entities}\n"
            content += f"    - Time: {stage.processing_time_seconds:.3f}s\n"
            content += f"    - Confidence Range: {stage.confidence_range[0]:.2f}-{stage.confidence_range[1]:.2f}\n"
            if stage.anonymization_applied:
                content += f"    - Anonymized: {stage.entities_anonymized}, Preserved: {stage.entities_preserved}\n"
            content += "\n"

        merge = stats.merge_analysis
        content += f"Entity Merge Analysis:\n"
        content += f"  • Total Before Merge: {merge.total_entities_before_merge}\n"
        content += f"  • Duplicates Found: {merge.duplicates_found}\n"
        content += f"  • Total After Merge: {merge.total_entities_after_merge}\n"
        content += f"  • Merge Quality Score: {merge.merge_quality_score:.2f}\n"

        return content

    def _format_compliance_report(self) -> str:
        """Format compliance report for display"""
        compliance = self.report.statistics.compliance_report

        content = "LEGAL COMPLIANCE REPORT\n"
        content += "=" * 25 + "\n\n"

        content += f"Configuration:\n"
        content += f"  • Factual Mode Active: {'Yes' if compliance.factual_mode_active else 'No'}\n"
        content += f"  • Anonymization Required: {'Yes' if compliance.anonymization_required else 'No'}\n\n"

        content += f"Transmission Safety Assessment:\n"
        content += f"  • Entities Ready for Transmission: {compliance.entities_ready_for_transmission}\n"
        content += f"  • Transmission Safe: {'✅ YES' if compliance.transmission_safe else '❌ NO'}\n"
        content += f"  • Risk Assessment: {compliance.risk_assessment}\n\n"

        if compliance.original_names_detected_in_output:
            content += f"⚠️  ORIGINAL NAMES DETECTED IN OUTPUT:\n"
            for name in compliance.original_names_detected_in_output:
                content += f"  • {name}\n"
            content += "\n"

        if compliance.compliance_warnings:
            content += f"Compliance Warnings:\n"
            for warning in compliance.compliance_warnings:
                content += f"  • {warning}\n"
            content += "\n"

        content += f"Legal Analysis:\n"
        if compliance.transmission_safe:
            content += "✅ All entities have been properly processed for external transmission.\n"
            content += "   The anonymization system has successfully neutralized sensitive content\n"
            content += "   while preserving factual information for analysis.\n"
        else:
            content += "❌ TRANSMISSION NOT SAFE: Original names detected in output.\n"
            content += "   Please review the anonymization settings or enable factual mode\n"
            content += "   only for scientific/educational content where preservation is legally justified.\n"

        content += f"\nCopyright Compliance Status: "
        if compliance.risk_assessment == "LOW":
            content += "✅ COMPLIANT - Safe for external API transmission"
        elif compliance.risk_assessment == "MEDIUM":
            content += "⚠️  REVIEW REQUIRED - Check warnings above"
        else:
            content += "❌ NON-COMPLIANT - Do not transmit to external APIs"

        return content

    def export_pdf(self) -> None:
        """Export report as PDF"""
        try:
            filename = self.report.generate_export_filename("pdf")
            file_path = filedialog.asksaveasfilename(
                title="Export Analysis Report as PDF",
                defaultextension=".pdf",
                initialvalue=filename,
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

            if file_path:
                self._export_as_pdf(file_path)
                messagebox.showinfo("Export Success", f"Report exported to: {Path(file_path).name}")

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            messagebox.showerror("Export Error", f"PDF export failed:\n{e}")

    def export_markdown(self) -> None:
        """Export report as Markdown"""
        try:
            filename = self.report.generate_export_filename("md")
            file_path = filedialog.asksaveasfilename(
                title="Export Analysis Report as Markdown",
                defaultextension=".md",
                initialvalue=filename,
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )

            if file_path:
                self._export_as_markdown(file_path)
                messagebox.showinfo("Export Success", f"Report exported to: {Path(file_path).name}")

        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            messagebox.showerror("Export Error", f"Markdown export failed:\n{e}")

    def export_json(self) -> None:
        """Export report as JSON"""
        try:
            filename = self.report.generate_export_filename("json")
            file_path = filedialog.asksaveasfilename(
                title="Export Analysis Report as JSON",
                defaultextension=".json",
                initialvalue=filename,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                self._export_as_json(file_path)
                messagebox.showinfo("Export Success", f"Report exported to: {Path(file_path).name}")

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            messagebox.showerror("Export Error", f"JSON export failed:\n{e}")

    def _export_as_pdf(self, file_path: str) -> None:
        """Export report content as PDF (placeholder implementation)"""
        # For now, export as text since PDF generation requires additional dependencies
        content = self._generate_full_report_text()

        # Save as text file with .pdf.txt extension for now
        text_path = file_path.replace('.pdf', '.pdf.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Note: Real PDF implementation would use libraries like reportlab
        messagebox.showinfo("PDF Export",
                           f"PDF export saved as text file: {Path(text_path).name}\n\n"
                           "Note: Full PDF support requires additional libraries.\n"
                           "Content has been saved in text format for now.")

    def _export_as_markdown(self, file_path: str) -> None:
        """Export report content as Markdown"""
        content = self._generate_markdown_report()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _export_as_json(self, file_path: str) -> None:
        """Export report data as JSON"""
        # Convert report to dictionary
        report_data = {
            "report_id": str(self.report.report_id),
            "generated_at": self.report.generated_at.isoformat(),
            "system_version": self.report.system_version,
            "statistics": self.report.statistics.dict(),
            "summary": self.report.get_summary_stats(),
            "local_transparency": self.report.get_local_transparency_section(),
            "transmission_preview": self.report.get_transmission_preview_section()
        }

        # Add semantic triples section if in factual mode
        summary = self.report.get_summary_stats()
        if summary.get('factual_mode', False):
            report_data["semantic_triples"] = self.report.get_semantic_triples_section()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_full_report_text(self) -> str:
        """Generate full report as text"""
        content = "LOCALINSIGHTENGINE - COMPREHENSIVE ANALYSIS REPORT\n"
        content += "=" * 55 + "\n\n"

        content += f"Generated: {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"System Version: {self.report.system_version}\n"
        content += f"Report ID: {self.report.report_id}\n\n"

        # Add all sections
        content += self._format_local_transparency_data(self.report.get_local_transparency_section())
        content += "\n" + "="*80 + "\n\n"

        content += self._format_transmission_preview_data(self.report.get_transmission_preview_section())
        content += "\n" + "="*80 + "\n\n"

        content += self._format_processing_stats()
        content += "\n" + "="*80 + "\n\n"

        # Add semantic triples section if in factual mode
        summary = self.report.get_summary_stats()
        if summary.get('factual_mode', False):
            content += self._format_semantic_triples_data(self.report.get_semantic_triples_section())
            content += "\n" + "="*80 + "\n\n"

        content += self._format_compliance_report()

        return content

    def setup_semantic_triples_tab(self) -> None:
        """Setup semantic triples tab (only visible in factual mode)"""
        # Check if factual mode is active
        summary = self.report.get_summary_stats()
        if not summary.get('factual_mode', False):
            return  # Don't add tab if not in factual mode

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🧠 Semantic Triples")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Header
        header = ttk.Label(frame, text="🧠 EXTRACTED SEMANTIC TRIPLES (FACTUAL MODE)",
                          font=("TkDefaultFont", 12, "bold"))
        header.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        # Get semantic triples data
        triples_data = self.report.get_semantic_triples_section()

        if "error" in triples_data:
            ttk.Label(frame, text=triples_data["error"]).grid(row=1, column=0, padx=10, pady=10)
            return

        # Create scrollable text area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Format and display semantic triples data
        content = self._format_semantic_triples_data(triples_data)
        text_area.insert(tk.END, content)
        text_area.config(state="disabled")

    def _format_semantic_triples_data(self, data: Dict[str, Any]) -> str:
        """Format semantic triples data for display"""
        content = f"{data['title']}\n"
        content += "=" * len(data['title']) + "\n\n"
        content += f"Total triples extracted: {data['total_triples']}\n"
        content += f"Triple confidence: {data['confidence_range'][0]:.2f} - {data['confidence_range'][1]:.2f}\n\n"

        if data['triples']:
            content += "EXTRACTED KNOWLEDGE TRIPLES:\n"
            content += "-" * 30 + "\n\n"

            for i, triple in enumerate(data['triples'][:20], 1):  # Show first 20 triples
                content += f"{i:2d}. {triple['subject']} → {triple['predicate']} → {triple['object']}\n"
                if triple.get('confidence'):
                    content += f"    Confidence: {triple['confidence']:.3f}\n"
                if triple.get('source_info'):
                    content += f"    Source: {triple['source_info']}\n"
                content += "\n"

            if len(data['triples']) > 20:
                content += f"... and {len(data['triples']) - 20} more triples\n\n"
        else:
            content += "No semantic triples extracted from this document.\n\n"

        content += f"\nNote: {data['note']}\n"
        content += "\nSemantic triples represent factual relationships extracted from the document.\n"
        content += "These structured facts enable advanced knowledge discovery and entity mapping.\n"

        return content

    def _generate_markdown_report(self) -> str:
        """Generate report in Markdown format"""
        stats = self.report.statistics

        content = "# LocalInsightEngine - Analysis Report\n\n"
        content += f"**Generated:** {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  \n"
        content += f"**System Version:** {self.report.system_version}  \n"
        content += f"**Document:** {stats.document_name}  \n\n"

        # Summary
        summary = self.report.get_summary_stats()
        content += "## Summary\n\n"
        content += f"- **Processing Time:** {summary['processing_time']}\n"
        content += f"- **Chunks Created:** {summary['chunks_created']}\n"
        content += f"- **Entities Found:** {summary['entities_total']}\n"
        content += f"- **Analysis Mode:** {'Factual' if summary['factual_mode'] else 'Standard'}\n"
        content += f"- **Transmission Status:** {'✅ Safe' if summary['transmission_safe'] else '❌ Risk'}\n\n"

        # Local Transparency
        local_data = self.report.get_local_transparency_section()
        content += "## 🔍 Local Transparency\n\n"
        content += f"**Total entities found:** {local_data['total_entities']}\n\n"

        for entity_type, info in local_data['entity_breakdown'].items():
            content += f"### {entity_type} ({info['count']} found)\n\n"
            for example in info['examples']:
                content += f"- {example}\n"
            content += "\n"

        # Transmission Preview
        trans_data = self.report.get_transmission_preview_section()
        content += "## 📡 Transmission Preview\n\n"
        content += f"**Status:** {trans_data['compliance_status']}  \n"
        content += f"**Entities for transmission:** {trans_data['total_entities']}\n\n"

        if trans_data['warnings']:
            content += "### ⚠️ Warnings\n\n"
            for warning in trans_data['warnings']:
                content += f"- {warning}\n"
            content += "\n"

        # Compliance
        compliance = stats.compliance_report
        content += "## ⚖️ Compliance Report\n\n"
        content += f"- **Factual Mode:** {'Yes' if compliance.factual_mode_active else 'No'}\n"
        content += f"- **Transmission Safe:** {'✅ Yes' if compliance.transmission_safe else '❌ No'}\n"
        content += f"- **Risk Assessment:** {compliance.risk_assessment}\n\n"

        # Semantic Triples (if factual mode)
        if summary.get('factual_mode', False):
            triples_data = self.report.get_semantic_triples_section()
            content += "## 🧠 Semantic Triples\n\n"
            content += f"**Total triples extracted:** {triples_data['total_triples']}\n\n"

            if triples_data['triples']:
                content += "### Knowledge Triples\n\n"
                for i, triple in enumerate(triples_data['triples'][:10], 1):  # First 10 for markdown
                    content += f"{i}. {triple['subject']} → {triple['predicate']} → {triple['object']}\n"
                content += "\n"

        # Processing Stats
        content += "## ⏱️ Processing Statistics\n\n"
        perf = stats.performance
        content += f"- **Total Processing Time:** {perf.total_processing_seconds:.3f}s\n"
        content += f"- **Entity Extraction Time:** {perf.entity_extraction_total_seconds:.3f}s\n"
        content += f"- **Chunks Created:** {stats.chunks_created}\n"
        content += f"- **Average Chunk Size:** {stats.average_chunk_size:.0f} chars\n\n"

        content += "---\n\n"
        content += "*Generated by LocalInsightEngine - Copyright-compliant document analysis*\n"

        return content

    def center_window(self) -> None:
        """Center the window on the parent"""
        self.window.update_idletasks()

        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Get this window size
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        self.window.geometry(f"+{x}+{y}")