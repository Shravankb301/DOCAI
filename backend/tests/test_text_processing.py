import unittest
import sys
import os
import re
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.ai_models import clean_text_for_preview, analyze_document_sections
from app.models.public_data import format_citations, search_regulatory_sources

class TestTextProcessing(unittest.TestCase):
    """Test cases for text processing functions."""
    
    def test_clean_text_for_preview_with_normal_text(self):
        """Test that normal text is preserved."""
        text = "This is a normal text that should be preserved as is."
        result = clean_text_for_preview(text)
        self.assertEqual(result, text)
    
    def test_clean_text_for_preview_with_binary_data(self):
        """Test that binary data is properly cleaned."""
        # Create text with binary/non-printable characters
        binary_text = "Normal text " + "".join(chr(i) for i in range(0, 32)) + " more text"
        result = clean_text_for_preview(binary_text)
        # Check that result doesn't contain control characters
        self.assertTrue(all(c.isprintable() or c.isspace() for c in result))
        # Check that it contains the readable parts
        self.assertIn("Normal text", result)
        self.assertIn("more text", result)
    
    def test_clean_text_for_preview_with_pdf_header(self):
        """Test that PDF header gibberish is properly cleaned."""
        pdf_header = "%PDF-1.6 % 443 0 obj <</Linearized 1/L 225361/O 445/E 130728/N 8/T 224926/H [ 521 358]>> endobj 466"
        result = clean_text_for_preview(pdf_header)
        # Check that result is readable and preserves meaningful parts
        self.assertNotEqual(result, "[Binary or non-text content]")
        self.assertIn("PDF", result)
    
    def test_clean_text_for_preview_with_xml_content(self):
        """Test that XML content is properly cleaned."""
        xml_content = "<xml><header>Title</header><body>Content with special chars: &lt;&gt;&amp;</body></xml>"
        result = clean_text_for_preview(xml_content)
        # Check that XML structure is preserved
        self.assertIn("<xml>", result)
        self.assertIn("<header>", result)
        self.assertIn("Title", result)
    
    def test_clean_text_for_preview_with_long_text(self):
        """Test that long text is properly truncated."""
        long_text = "A" * 200
        result = clean_text_for_preview(long_text, max_length=100)
        self.assertEqual(len(result), 103)  # 100 chars + "..."
        self.assertTrue(result.endswith("..."))
    
    def test_clean_text_for_preview_with_empty_text(self):
        """Test that empty text returns appropriate placeholder."""
        result = clean_text_for_preview("")
        self.assertEqual(result, "[Binary or non-text content]")
    
    def test_clean_text_for_preview_with_whitespace_only(self):
        """Test that whitespace-only text returns appropriate placeholder."""
        result = clean_text_for_preview("   \t\n   ")
        self.assertEqual(result, "[Binary or non-text content]")
    
    def test_analyze_document_sections_with_mixed_content(self):
        """Test that document sections are properly analyzed with mixed content."""
        # Create a document with normal text and some binary-like content
        text = "This is a normal paragraph.\n\n" + \
               "%PDF-1.6 % 443 0 obj <</Linearized 1/L 225361/O 445/E 130728/N 8/T 224926/H [ 521 358]>> endobj 466\n\n" + \
               "Another normal paragraph with important information."
        
        # Set a small section size to ensure multiple sections
        section_size = 50
        results = analyze_document_sections(text, section_size)
        
        # Check that we have multiple sections
        self.assertTrue(len(results) > 1)
        
        # Check that each section has the required fields
        for section in results:
            self.assertIn("section_number", section)
            self.assertIn("section_text", section)
            self.assertIn("status", section)
            self.assertIn("confidence", section)
            
            # Check that section_text is readable
            self.assertTrue(all(c.isprintable() or c.isspace() for c in section["section_text"]))
    
    def test_format_citations_with_complete_data(self):
        """Test that citations are properly formatted with complete data."""
        sources = [
            {
                "source_name": "General Data Protection Regulation (GDPR)",
                "source_url": "https://gdpr-info.eu/",
                "source_description": "Comprehensive data privacy regulation in the EU.",
                "relevance_score": 0.85,
                "matched_categories": ["data_privacy", "personal_data"],
                "organization": "European Union",
                "publication_date": "2018-05-25"
            }
        ]
        
        citations = format_citations(sources)
        
        # Check that we have one citation
        self.assertEqual(len(citations), 1)
        
        # Check that citation has all required fields
        citation = citations[0]
        self.assertIn("citation_number", citation)
        self.assertIn("source_name", citation)
        self.assertIn("source_url", citation)
        self.assertIn("source_description", citation)
        self.assertIn("relevance_score", citation)
        self.assertIn("citation_text", citation)
        self.assertIn("reference_info", citation)
        
        # Check that citation text includes organization and publication date
        self.assertIn("European Union", citation["citation_text"])
        self.assertIn("2018-05-25", citation["citation_text"])
        
        # Check that reference_info has all required fields
        ref_info = citation["reference_info"]
        self.assertIn("title", ref_info)
        self.assertIn("url", ref_info)
        self.assertIn("description", ref_info)
        self.assertIn("access_date", ref_info)
        self.assertIn("categories", ref_info)
        self.assertIn("type", ref_info)
        
        # Check that categories are preserved
        self.assertEqual(ref_info["categories"], ["data_privacy", "personal_data"])
    
    def test_format_citations_with_minimal_data(self):
        """Test that citations are properly formatted with minimal data."""
        sources = [
            {
                "source_name": "Test Source",
                "source_url": "https://example.com",
                "source_description": "Test description",
                "relevance_score": 0.5
            }
        ]
        
        citations = format_citations(sources)
        
        # Check that we have one citation
        self.assertEqual(len(citations), 1)
        
        # Check that citation has all required fields
        citation = citations[0]
        self.assertIn("citation_number", citation)
        self.assertIn("source_name", citation)
        self.assertIn("source_url", citation)
        self.assertIn("source_description", citation)
        self.assertIn("relevance_score", citation)
        self.assertIn("citation_text", citation)
        
        # Check that citation text includes domain extracted from URL
        self.assertIn("example.com", citation["citation_text"])
        
        # Check that reference_info has all required fields even with minimal data
        self.assertIn("reference_info", citation)
        ref_info = citation["reference_info"]
        self.assertIn("title", ref_info)
        self.assertIn("url", ref_info)
        self.assertIn("description", ref_info)
        self.assertIn("access_date", ref_info)
        self.assertIn("type", ref_info)

if __name__ == "__main__":
    unittest.main() 