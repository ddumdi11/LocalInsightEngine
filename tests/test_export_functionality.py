"""
Unit tests for export functionality.
LocalInsightEngine v0.1.0 - Export Functionality Tests
"""

import sys
import tempfile
import json
from pathlib import Path
import unittest

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.main import LocalInsightEngine
from local_insight_engine.services.export.json_exporter import JsonExporter
from local_insight_engine.services.export.export_manager import ExportManager


class TestExportFunctionality(unittest.TestCase):
    """Test cases for document export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = LocalInsightEngine()
        self.json_exporter = JsonExporter()
        self.export_manager = ExportManager()
        
        # Sample texts for testing
        self.german_sample = """
        Dies ist ein deutsches Testdokument für die LocalInsightEngine.
        
        Hauptthemen:
        1. Künstliche Intelligenz und maschinelles Lernen
        2. Datenverarbeitung und Textanalyse
        3. Urheberrechtskonformität bei der Dokumentenanalyse
        
        Wichtige Aspekte:
        - Named Entity Recognition erkennt Personen wie Max Mustermann
        - Organisationen wie die Deutsche Forschungsgemeinschaft werden identifiziert
        - Orte wie Berlin, München und Hamburg sind relevant
        - Technologien wie spaCy und Claude werden verwendet
        
        Schlussfolgerungen:
        Das System analysiert Inhalte ohne Urheberrechtsverletzungen.
        Die Neutralisierung funktioniert korrekt.
        """
        
        self.english_sample = """
        This is an English test document for LocalInsightEngine analysis.
        
        Main Topics:
        1. Artificial intelligence and machine learning applications
        2. Natural language processing and text analysis
        3. Copyright-compliant document processing
        
        Key Points:
        - Named Entity Recognition identifies people like John Smith
        - Organizations such as MIT and Stanford University are recognized  
        - Locations including New York, London, and Tokyo are relevant
        - Technologies like Python and Claude AI are mentioned
        
        Conclusions:
        The system processes content while maintaining copyright compliance.
        Text neutralization works as designed.
        """
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_json_export_german_text(self):
        """Test JSON export with German text sample."""
        print("\n[TEST] JSON Export - German Text")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.german_sample)
            test_file = Path(f.name)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "german_analysis"
                
                # Test analyze_and_export method
                results = self.engine.analyze_and_export(
                    document_path=test_file,
                    output_path=output_path,
                    formats=["json"]
                )
                
                # Verify export was successful
                self.assertTrue(results['export_results']['json'], "JSON export should succeed")
                self.assertIn('json', results['export_paths'], "JSON path should be in results")
                
                json_path = results['export_paths']['json']
                self.assertTrue(json_path.exists(), f"JSON file should exist at {json_path}")
                
                # Validate JSON structure
                with open(json_path, 'r', encoding='utf-8') as f:
                    exported_data = json.load(f)
                
                self._validate_json_structure(exported_data)
                
                # Check German-specific content
                self.assertEqual(
                    exported_data['document']['metadata']['filename'],
                    test_file.name,
                    "Filename should match"
                )
                
                print("✓ German text JSON export successful")
                
        finally:
            test_file.unlink()
    
    def test_json_export_english_text(self):
        """Test JSON export with English text sample."""
        print("\n[TEST] JSON Export - English Text")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.english_sample)
            test_file = Path(f.name)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "english_analysis"
                
                results = self.engine.analyze_and_export(
                    document_path=test_file,
                    output_path=output_path,
                    formats=["json"]
                )
                
                self.assertTrue(results['export_results']['json'])
                
                json_path = results['export_paths']['json']
                with open(json_path, 'r', encoding='utf-8') as f:
                    exported_data = json.load(f)
                
                self._validate_json_structure(exported_data)
                
                # Check for English NER results (should have entities)
                entities = exported_data['text_processing']['entity_summary']
                self.assertGreater(len(entities), 0, "Should find entities in English text")
                
                print("✓ English text JSON export successful")
                
        finally:
            test_file.unlink()
    
    def test_export_manager_functionality(self):
        """Test export manager methods."""
        print("\n[TEST] Export Manager Functionality")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.german_sample)
            test_file = Path(f.name)
        
        try:
            # Test analyze without export first
            document = self.engine.document_loader.load(test_file)
            processed_data = self.engine.text_processor.process(document)
            analysis = self.engine.llm_client.analyze(processed_data)
            
            # Test export summary
            summary = self.export_manager.get_export_summary(
                analysis, processed_data, document
            )
            
            self.assertIn('document_info', summary)
            self.assertIn('processing_results', summary) 
            self.assertIn('analysis_results', summary)
            self.assertIn('export_options', summary)
            
            # Test filename generation without timestamp
            filename = self.export_manager.generate_output_filename(document, include_timestamp=False)
            self.assertIsInstance(filename, Path)
            self.assertTrue(str(filename).endswith('_analysis'))
            
            # Test filename generation with timestamp
            filename_with_timestamp = self.export_manager.generate_output_filename(document, include_timestamp=True)
            self.assertIsInstance(filename_with_timestamp, Path)
            self.assertTrue('_analysis_' in str(filename_with_timestamp))
            self.assertGreater(len(str(filename_with_timestamp)), len(str(filename)))
            
            print("✓ Export manager functionality working")
            
        finally:
            test_file.unlink()
    
    def test_json_structure_compliance(self):
        """Test that JSON export maintains copyright compliance markers."""
        print("\n[TEST] JSON Copyright Compliance Structure")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Simple test document for compliance testing.")
            test_file = Path(f.name)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "compliance_test"
                
                results = self.engine.analyze_and_export(
                    test_file, output_path, ["json"]
                )
                
                json_path = results['export_paths']['json']
                with open(json_path, 'r', encoding='utf-8') as f:
                    exported_data = json.load(f)
                
                # Check compliance section
                compliance = exported_data.get('compliance', {})
                self.assertTrue(
                    compliance.get('copyright_compliant', False),
                    "Should be marked as copyright compliant"
                )
                self.assertFalse(
                    compliance.get('contains_original_text', True),
                    "Should not contain original text"
                )
                self.assertTrue(
                    compliance.get('neutralization_applied', False),
                    "Should have neutralization applied"
                )
                
                print("✓ Copyright compliance markers correct")
                
        finally:
            test_file.unlink()
    
    def _validate_json_structure(self, exported_data):
        """Validate the structure of exported JSON data."""
        required_top_level = [
            "export_metadata", "document", "text_processing", 
            "analysis", "compliance"
        ]
        
        for key in required_top_level:
            self.assertIn(key, exported_data, f"Missing top-level key: {key}")
        
        # Check export metadata
        metadata = exported_data['export_metadata']
        self.assertIn('export_timestamp', metadata)
        self.assertIn('export_version', metadata)
        self.assertIn('localinsightengine_version', metadata)
        self.assertEqual(metadata['format'], 'json')
        
        # Check document section
        document = exported_data['document']
        self.assertIn('metadata', document)
        self.assertIn('processing_stats', document)
        
        # Check text processing section
        text_processing = exported_data['text_processing']
        self.assertIn('key_themes', text_processing)
        self.assertIn('entity_summary', text_processing)
        self.assertIn('chunk_statistics', text_processing)
        
        # Check analysis section
        analysis = exported_data['analysis']
        required_analysis_keys = [
            'status', 'model', 'confidence_score', 'completeness_score',
            'executive_summary', 'insights', 'questions'
        ]
        for key in required_analysis_keys:
            self.assertIn(key, analysis, f"Missing analysis key: {key}")
        
        # Check that insights and questions are lists
        self.assertIsInstance(analysis['insights'], list)
        self.assertIsInstance(analysis['questions'], list)
        
        print("✓ JSON structure validation passed")


if __name__ == '__main__':
    print("LocalInsightEngine - Export Functionality Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)