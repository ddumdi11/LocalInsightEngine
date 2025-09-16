"""
Critical Paths Coverage Tests for LocalInsightEngine.
LocalInsightEngine v0.1.1 - Comprehensive Coverage of Critical Code Paths

FOCUS: 95% Coverage Goal for data_layer and processing_hub critical paths
COVERAGE: All major code branches, error conditions, and edge cases in core modules
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock, mock_open
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.data_layer.document_loader import DocumentLoader
from local_insight_engine.services.processing_hub.spacy_entity_extractor import SpacyEntityExtractor
from local_insight_engine.services.processing_hub.text_processor import TextProcessor
# neutralize_entities function is not available in neutralization_utils
# from local_insight_engine.services.processing_hub.neutralization_utils import neutralize_entities
from local_insight_engine.models.document import Document, DocumentMetadata
from local_insight_engine.models.text_data import TextChunk, ProcessedText


class TestDocumentLoaderCriticalPaths(unittest.TestCase):
    """Test all critical paths in DocumentLoader."""

    def setUp(self):
        self.loader = DocumentLoader()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_file_type_detection_all_paths(self):
        """Test all file type detection code paths."""
        # Test 1: PDF detection
        pdf_content = b'%PDF-1.4\nPDF content here'
        pdf_file = self.test_dir / "test.pdf"
        pdf_file.write_bytes(pdf_content)

        detected_type = self.loader._detect_actual_file_type(pdf_file)
        self.assertEqual(detected_type, "pdf")

        # Test 2: DOCX detection (ZIP-based)
        with patch('local_insight_engine.services.data_layer.document_loader.DocxDocument') as mock_docx:
            mock_docx.return_value = Mock()  # Successful DOCX parsing

            zip_file = self.test_dir / "test.docx"
            zip_file.write_bytes(b'PK\x03\x04')  # ZIP signature

            detected_type = self.loader._detect_actual_file_type(zip_file)
            self.assertEqual(detected_type, "docx")

        # Test 3: EPUB detection (ZIP-based but different)
        with patch('local_insight_engine.services.data_layer.document_loader.DocxDocument') as mock_docx:
            mock_docx.side_effect = Exception("Not a DOCX")  # Fail DOCX, try EPUB

            epub_file = self.test_dir / "test.epub"
            epub_content = b'PK\x03\x04\x00\x00\x00\x00mimetypeapplication/epub+zip'
            epub_file.write_bytes(epub_content)

            detected_type = self.loader._detect_actual_file_type(epub_file)
            self.assertEqual(detected_type, "epub")

        # Test 4: Text file detection (UTF-8)
        text_file = self.test_dir / "test.txt"
        text_file.write_text("Plain text content", encoding='utf-8')

        detected_type = self.loader._detect_actual_file_type(text_file)
        self.assertEqual(detected_type, "txt")

        # Test 5: Text file with Latin-1 encoding
        latin_file = self.test_dir / "latin.txt"
        with open(latin_file, 'w', encoding='latin-1') as f:
            f.write("Latin-1 content with ümlaut")

        detected_type = self.loader._detect_actual_file_type(latin_file)
        self.assertEqual(detected_type, "txt")

        # Test 6: Unknown file type
        binary_file = self.test_dir / "unknown.bin"
        binary_file.write_bytes(b'\x89\x50\x4E\x47')  # PNG signature (not supported)

        detected_type = self.loader._detect_actual_file_type(binary_file)
        self.assertEqual(detected_type, "unknown")

        # Test 7: File that can't be read (permission error simulation)
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            detected_type = self.loader._detect_actual_file_type(text_file)
            self.assertEqual(detected_type, "unknown")

    def test_validate_file_type_all_paths(self):
        """Test all file type validation code paths."""
        # Test 1: Matching extension and content
        pdf_file = self.test_dir / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4\ncontent')

        detected_type, matches = self.loader._validate_file_type(pdf_file)
        self.assertEqual(detected_type, "pdf")
        self.assertTrue(matches)

        # Test 2: Mismatched extension and content
        fake_pdf = self.test_dir / "fake.pdf"
        fake_pdf.write_text("This is actually text", encoding='utf-8')

        detected_type, matches = self.loader._validate_file_type(fake_pdf)
        self.assertEqual(detected_type, "txt")
        self.assertFalse(matches)

    def test_load_method_all_error_paths(self):
        """Test all error paths in the load method."""
        # Test 1: File does not exist
        non_existent = self.test_dir / "does_not_exist.txt"

        with self.assertRaises(FileNotFoundError):
            self.loader.load(non_existent)

        # Test 2: Unsupported file extension
        unsupported_file = self.test_dir / "test.xyz"
        unsupported_file.touch()

        with self.assertRaises(ValueError) as cm:
            self.loader.load(unsupported_file)
        self.assertIn("Unsupported format", str(cm.exception))

        # Test 3: Detected type is unknown/unsupported
        with patch.object(self.loader, '_detect_actual_file_type', return_value="unknown"):
            supported_file = self.test_dir / "test.txt"
            supported_file.write_text("content", encoding='utf-8')

            with self.assertRaises(ValueError) as cm:
                self.loader.load(supported_file)
            self.assertIn("Unsupported or undetected", str(cm.exception))

    def test_pdf_loading_error_paths(self):
        """Test error handling in PDF loading."""
        pdf_file = self.test_dir / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4\ncontent')

        # Test 1: PyPDF2 reader fails
        with patch('local_insight_engine.services.data_layer.document_loader.PdfReader') as mock_reader:
            mock_reader.side_effect = Exception("PDF parsing failed")

            with self.assertRaises(Exception):
                self.loader._load_pdf(pdf_file)

        # Test 2: PDF with no pages
        with patch('local_insight_engine.services.data_layer.document_loader.PdfReader') as mock_reader:
            mock_instance = Mock()
            mock_instance.pages = []  # No pages
            mock_instance.metadata = None
            mock_reader.return_value = mock_instance

            document = self.loader._load_pdf(pdf_file)
            self.assertEqual(document.metadata.page_count, 0)

        # Test 3: PDF with metadata
        with patch('local_insight_engine.services.data_layer.document_loader.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test content"

            mock_instance = Mock()
            mock_instance.pages = [mock_page]
            mock_instance.metadata = {'/Title': 'Test Document', '/Author': 'Test Author'}
            mock_reader.return_value = mock_instance

            document = self.loader._load_pdf(pdf_file)
            self.assertEqual(document.metadata.title, 'Test Document')
            self.assertEqual(document.metadata.author, 'Test Author')

    def test_text_loading_error_paths(self):
        """Test error handling in text file loading."""
        text_file = self.test_dir / "test.txt"

        # Test 1: File reading fails
        with patch('builtins.open', side_effect=IOError("Read error")):
            with self.assertRaises(IOError):
                self.loader._load_text(text_file)

        # Test 2: Complex paragraph parsing
        complex_text = "Para 1\n\nPara 2\n\n\n\nPara 3\n\n   \n\nPara 4"
        text_file.write_text(complex_text, encoding='utf-8')

        document = self.loader._load_text(text_file)
        # Should handle multiple empty lines and whitespace-only lines
        self.assertGreater(len(document.paragraph_mapping), 0)

    def test_epub_loading_error_paths(self):
        """Test error handling in EPUB loading."""
        epub_file = self.test_dir / "test.epub"
        epub_file.write_bytes(b'fake epub content')

        # Test 1: EPUB reading fails
        with patch('local_insight_engine.services.data_layer.document_loader.epub.read_epub') as mock_epub:
            mock_epub.side_effect = Exception("EPUB parsing failed")

            with self.assertRaises(Exception):
                self.loader._load_epub(epub_file)

        # Test 2: EPUB with complex structure
        with patch('local_insight_engine.services.data_layer.document_loader.epub.read_epub') as mock_epub:
            with patch('local_insight_engine.services.data_layer.document_loader.ebooklib.ITEM_DOCUMENT', 9):
                # Mock book structure
                mock_item1 = Mock()
                mock_item1.get_type.return_value = 9  # ITEM_DOCUMENT
                mock_item1.content = b'<html><h1>Chapter 1</h1><p>Content 1</p></html>'

                mock_item2 = Mock()
                mock_item2.get_type.return_value = 8  # Not a document
                mock_item2.content = b'<html><p>Not a chapter</p></html>'

                mock_item3 = Mock()
                mock_item3.get_type.return_value = 9  # ITEM_DOCUMENT
                mock_item3.content = b'<html><h2>Chapter 2</h2><p>Content 2</p></html>'

                mock_book = Mock()
                mock_book.get_items.return_value = [mock_item1, mock_item2, mock_item3]
                mock_book.get_metadata.return_value = [('Test Book', {})]
                mock_epub.return_value = mock_book

                with patch('local_insight_engine.services.data_layer.document_loader.BeautifulSoup') as mock_bs:
                    def mock_soup_side_effect(content, parser):
                        soup = Mock()
                        if b'Chapter 1' in content:
                            soup.get_text.return_value = "Chapter 1\n\nContent 1"
                            title_tag = Mock()
                            title_tag.get_text.return_value = "Chapter 1"
                            soup.find.return_value = title_tag
                        elif b'Chapter 2' in content:
                            soup.get_text.return_value = "Chapter 2\n\nContent 2"
                            soup.find.return_value = None  # No title tag
                        return soup

                    mock_bs.side_effect = mock_soup_side_effect

                    document = self.loader._load_epub(epub_file)
                    self.assertEqual(document.metadata.page_count, 2)  # Only 2 document items

    def test_docx_loading_error_paths(self):
        """Test error handling in DOCX loading."""
        docx_file = self.test_dir / "test.docx"
        docx_file.write_bytes(b'fake docx content')

        # Test 1: DOCX reading fails
        with patch('local_insight_engine.services.data_layer.document_loader.DocxDocument') as mock_docx:
            mock_docx.side_effect = Exception("DOCX parsing failed")

            with self.assertRaises(Exception):
                self.loader._load_docx(docx_file)

        # Test 2: DOCX with metadata
        with patch('local_insight_engine.services.data_layer.document_loader.DocxDocument') as mock_docx:
            mock_para1 = Mock()
            mock_para1.text = "Paragraph 1"
            mock_para2 = Mock()
            mock_para2.text = ""  # Empty paragraph (should be skipped)
            mock_para3 = Mock()
            mock_para3.text = "Paragraph 3"

            mock_doc = Mock()
            mock_doc.paragraphs = [mock_para1, mock_para2, mock_para3]

            # Mock core properties
            mock_core_props = Mock()
            mock_core_props.title = "Test Document"
            mock_core_props.author = "Test Author"
            mock_doc.core_properties = mock_core_props

            mock_docx.return_value = mock_doc

            document = self.loader._load_docx(docx_file)
            self.assertEqual(document.metadata.title, "Test Document")
            self.assertEqual(document.metadata.author, "Test Author")
            # Should have 2 non-empty paragraphs
            self.assertEqual(len(document.paragraph_mapping), 2)

    def test_utility_methods_coverage(self):
        """Test utility methods for complete coverage."""
        # Test _is_supported_format
        self.assertTrue(self.loader._is_supported_format(Path("test.pdf")))
        self.assertTrue(self.loader._is_supported_format(Path("test.txt")))
        self.assertFalse(self.loader._is_supported_format(Path("test.xyz")))

        # Test _get_file_format
        self.assertEqual(self.loader._get_file_format(Path("test.pdf")), "pdf")
        self.assertEqual(self.loader._get_file_format(Path("test.TXT")), "txt")  # Case insensitive

        # Test get_file_type_info
        text_file = self.test_dir / "test.txt"
        text_file.write_text("content", encoding='utf-8')

        info = self.loader.get_file_type_info(text_file)
        self.assertIn('extension', info)
        self.assertIn('detected_type', info)
        self.assertIn('matches', info)
        self.assertIn('supported', info)


class TestSpacyEntityExtractorCriticalPaths(unittest.TestCase):
    """Test all critical paths in SpacyEntityExtractor."""

    def setUp(self):
        # Mock spaCy to avoid model dependencies
        self.mock_patcher = patch('spacy.load')
        mock_spacy_load = self.mock_patcher.start()

        self.mock_de_nlp = Mock()
        self.mock_en_nlp = Mock()

        def mock_load_side_effect(model_name):
            if 'de_' in model_name:
                return self.mock_de_nlp
            else:
                return self.mock_en_nlp

        mock_spacy_load.side_effect = mock_load_side_effect
        self.extractor = SpacyEntityExtractor()

    def tearDown(self):
        self.mock_patcher.stop()

    def test_initialization_paths(self):
        """Test all initialization code paths."""
        # Test successful initialization (already done in setUp)
        self.assertIsNotNone(self.extractor.german_nlp)

        # Test initialization failure
        with patch('spacy.load', side_effect=OSError("Model not found")):
            with self.assertRaises(OSError):
                SpacyEntityExtractor()

    def test_extract_and_neutralize_all_paths(self):
        """Test all paths in extract_and_neutralize method."""
        # Test 1: Empty/None input
        result = self.extractor.extract_and_neutralize("")
        self.assertEqual(result, "")

        # Test 2: Normal entity extraction
        test_text = "John Smith works at CANARY_COMPANY_123 in Berlin."

        # Mock entity extraction
        mock_entity1 = Mock()
        mock_entity1.text = "John Smith"
        mock_entity1.label_ = "PERSON"

        mock_entity2 = Mock()
        mock_entity2.text = "Berlin"
        mock_entity2.label_ = "GPE"  # Geopolitical entity

        mock_doc = Mock()
        mock_doc.ents = [mock_entity1, mock_entity2]
        self.mock_de_nlp.return_value = mock_doc

        result = self.extractor.extract_and_neutralize(test_text)

        # Should neutralize suspicious identifiers and entities
        self.assertNotIn("CANARY_COMPANY_123", result)
        # John Smith should be neutralized as a person
        self.assertNotIn("John Smith", result)

    def test_neutralize_suspicious_identifiers_all_patterns(self):
        """Test all patterns in _neutralize_suspicious_identifiers."""
        # Test 1: CANARY patterns
        text_with_canary = "Text with CANARY_TEST_123 identifier"
        result = self.extractor._neutralize_suspicious_identifiers(text_with_canary)
        self.assertNotIn("CANARY_TEST_123", result)

        # Test 2: TEST patterns
        text_with_test = "Text with TEST_IDENTIFIER_456 marker"
        result = self.extractor._neutralize_suspicious_identifiers(text_with_test)
        self.assertNotIn("TEST_IDENTIFIER_456", result)

        # Test 3: DEBUG patterns
        text_with_debug = "Debug marker DEBUG_TRACE_789 here"
        result = self.extractor._neutralize_suspicious_identifiers(text_with_debug)
        self.assertNotIn("DEBUG_TRACE_789", result)

        # Test 4: Long alphanumeric identifiers
        text_with_long_id = "ID ABC123DEF456GHI789JKL000 found"
        result = self.extractor._neutralize_suspicious_identifiers(text_with_long_id)
        self.assertNotIn("ABC123DEF456GHI789JKL000", result)

        # Test 5: Legitimate terms that should NOT be neutralized
        legitimate_text = "Phosphatidylserin and Vitamin B3 are important"
        result = self.extractor._neutralize_suspicious_identifiers(legitimate_text)
        self.assertIn("Phosphatidylserin", result)
        self.assertIn("Vitamin B3", result)

        # Test 6: Empty text
        empty_result = self.extractor._neutralize_suspicious_identifiers("")
        self.assertEqual(empty_result, "")

    def test_neutralize_entities_all_paths(self):
        """Test all paths in neutralize_entities method."""
        # Test 1: Text with various entity types
        test_text = "Dr. John Smith from Microsoft met with Angela Merkel in Berlin."

        # Mock comprehensive entity extraction
        entities = [
            Mock(text="Dr. John Smith", label_="PERSON"),
            Mock(text="Microsoft", label_="ORG"),
            Mock(text="Angela Merkel", label_="PERSON"),
            Mock(text="Berlin", label_="GPE")
        ]

        mock_doc = Mock()
        mock_doc.ents = entities
        self.mock_de_nlp.return_value = mock_doc

        result = self.extractor.neutralize_entities(test_text, entities)

        # All named entities should be neutralized
        self.assertNotIn("John Smith", result)
        self.assertNotIn("Microsoft", result)
        self.assertNotIn("Angela Merkel", result)
        # But common place names might be kept with "[LOCATION]"
        self.assertIn("[PERSON]", result)
        self.assertIn("[ORGANIZATION]", result)

    def test_language_detection_fallback(self):
        """Test language detection and fallback behavior."""
        # Test with text that might trigger English model (if available)
        english_text = "The quick brown fox jumps over the lazy dog."

        mock_doc = Mock()
        mock_doc.ents = []
        self.mock_de_nlp.return_value = mock_doc

        result = self.extractor.extract_and_neutralize(english_text)
        self.assertIsInstance(result, str)

        # Should use German model even for English text (current implementation)
        self.mock_de_nlp.assert_called()

    def test_error_handling_in_entity_extraction(self):
        """Test error handling during entity extraction."""
        test_text = "Test text for error handling"

        # Test 1: spaCy processing fails
        self.mock_de_nlp.side_effect = Exception("spaCy processing error")

        with self.assertRaises(Exception):
            self.extractor.extract_and_neutralize(test_text)

        # Reset mock
        self.mock_de_nlp.side_effect = None

        # Test 2: Entity processing fails but extraction continues
        mock_entity = Mock()
        mock_entity.text = "Valid Entity"
        mock_entity.label_ = "PERSON"

        # Mock doc with entity that causes issues during neutralization
        mock_doc = Mock()
        mock_doc.ents = [mock_entity]
        self.mock_de_nlp.return_value = mock_doc

        # Should handle individual entity errors gracefully
        result = self.extractor.extract_and_neutralize(test_text)
        self.assertIsInstance(result, str)


class TestTextProcessorCriticalPaths(unittest.TestCase):
    """Test all critical paths in TextProcessor."""

    def setUp(self):
        # Mock dependencies
        with patch('local_insight_engine.services.processing_hub.spacy_entity_extractor.SpacyEntityExtractor'):
            with patch('local_insight_engine.services.processing_hub.statement_extractor.StatementExtractor'):
                self.processor = TextProcessor(chunk_size=100, chunk_overlap=20)

    def test_initialization_parameters(self):
        """Test TextProcessor initialization with various parameters."""
        # Test with default parameters
        processor1 = TextProcessor()
        self.assertEqual(processor1.chunk_size, 1000)  # Default
        self.assertEqual(processor1.chunk_overlap, 200)  # Default

        # Test with custom parameters
        processor2 = TextProcessor(chunk_size=500, chunk_overlap=100)
        self.assertEqual(processor2.chunk_size, 500)
        self.assertEqual(processor2.chunk_overlap, 100)

        # Test with edge case parameters
        processor3 = TextProcessor(chunk_size=1, chunk_overlap=0)
        self.assertEqual(processor3.chunk_size, 1)
        self.assertEqual(processor3.chunk_overlap, 0)

    def test_process_method_all_paths(self):
        """Test all code paths in the process method."""
        # Create mock document
        metadata = DocumentMetadata(
            file_path=Path("test.txt"),
            file_size=1000,
            file_format="txt",
            word_count=100
        )

        # Test 1: Document with normal content
        document = Document(
            metadata=metadata,
            text_content="This is a test document. " * 10,  # 250 chars
            page_mapping={1: (0, 250)},
            paragraph_mapping={0: (0, 125), 1: (125, 250)},
            section_mapping={}
        )

        # Mock the chunking and processing
        with patch.object(self.processor, '_create_chunks') as mock_chunks:
            mock_chunk = TextChunk(
                chunk_id=0,
                original_content="Test chunk",
                neutralized_content="Neutralized chunk",
                page_range=(1, 1),
                paragraph_range=(0, 0),
                section_info={},
                entities=[],
                statements=[]
            )
            mock_chunks.return_value = [mock_chunk]

            result = self.processor.process(document)

            self.assertIsInstance(result, ProcessedText)
            self.assertEqual(len(result.chunks), 1)

        # Test 2: Empty document
        empty_document = Document(
            metadata=metadata,
            text_content="",
            page_mapping={},
            paragraph_mapping={},
            section_mapping={}
        )

        result = self.processor.process(empty_document)
        self.assertIsInstance(result, ProcessedText)

        # Test 3: Document with only whitespace
        whitespace_document = Document(
            metadata=metadata,
            text_content="   \n\n   \t\t   ",
            page_mapping={1: (0, 15)},
            paragraph_mapping={},
            section_mapping={}
        )

        result = self.processor.process(whitespace_document)
        self.assertIsInstance(result, ProcessedText)


class TestNeutralizationUtilsCriticalPaths(unittest.TestCase):
    """Test all critical paths in neutralization utilities."""

    def test_neutralization_utils_functions(self):
        """Test available functions in neutralization_utils."""
        from local_insight_engine.services.processing_hub.neutralization_utils import (
            is_sufficiently_neutralized,
            create_abstract_version
        )

        # Test 1: is_sufficiently_neutralized - similar texts
        original = "John Smith works at Microsoft"
        neutralized = "John Smith works at Microsoft"  # Same text
        self.assertFalse(is_sufficiently_neutralized(original, neutralized))

        # Test 2: is_sufficiently_neutralized - different texts
        neutralized_different = "A person works at a company"
        self.assertTrue(is_sufficiently_neutralized(original, neutralized_different))

        # Test 3: create_abstract_version - German
        statement = "Diese Studie zeigt 75% Verbesserung der Methode"
        result = create_abstract_version(statement, "german")
        self.assertIsInstance(result, str)
        self.assertNotIn("75%", result)  # Should not contain original numbers

        # Test 4: create_abstract_version - English
        statement_en = "This research shows 50% improvement in the system"
        result_en = create_abstract_version(statement_en, "english")
        self.assertIsInstance(result_en, str)
        self.assertNotIn("50%", result_en)  # Should not contain original numbers


if __name__ == '__main__':
    print("LocalInsightEngine - Critical Paths Coverage Tests")
    print("=" * 60)
    print("TARGET: 95% Coverage of data_layer and processing_hub")
    print("SCOPE: All major code branches, error conditions, edge cases")
    print()

    unittest.main(verbosity=2, buffer=True)