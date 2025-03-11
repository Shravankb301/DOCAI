"""
Test script for regulatory agents functionality.
"""

import sys
import os
import unittest
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the regulatory agents module
try:
    from app.models.regulatory_agents import search_with_agents, RegulatorySearchAgent
    from app.models.public_data import search_regulatory_sources, format_citations
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

class TestRegulatoryAgents(unittest.TestCase):
    """Test cases for regulatory agents functionality."""
    
    def test_search_regulatory_sources(self):
        """Test the basic search_regulatory_sources function."""
        # Test with a simple query
        results = search_regulatory_sources("data privacy and GDPR compliance")
        
        # Check that we got some results
        self.assertTrue(len(results) > 0, "Should return at least one result")
        
        # Check that the results are sorted by relevance
        if len(results) > 1:
            self.assertGreaterEqual(
                results[0]["relevance_score"], 
                results[1]["relevance_score"],
                "Results should be sorted by relevance score"
            )
        
        # Check that the GDPR source is in the results
        gdpr_found = any("GDPR" in result["source_name"] for result in results)
        self.assertTrue(gdpr_found, "GDPR should be in the results")
    
    def test_format_citations(self):
        """Test the format_citations function."""
        # Create a sample source
        sources = [{
            "source_name": "Test Regulation",
            "source_url": "https://example.com/regulation",
            "source_description": "A test regulation for unit testing",
            "relevance_score": 0.8,
            "matched_categories": ["test", "regulation"]
        }]
        
        # Format the citations
        citations = format_citations(sources)
        
        # Check that we got a citation
        self.assertEqual(len(citations), 1, "Should return one citation")
        
        # Check that the citation has the expected fields
        citation = citations[0]
        self.assertEqual(citation["source_name"], "Test Regulation")
        self.assertEqual(citation["source_url"], "https://example.com/regulation")
        self.assertTrue("citation_text" in citation, "Citation should have citation_text")
        self.assertTrue("reference_info" in citation, "Citation should have reference_info")
    
    @unittest.skipIf(not AGENTS_AVAILABLE, "Regulatory agents not available")
    def test_regulatory_search_agent(self):
        """Test the RegulatorySearchAgent class."""
        # Create an agent
        agent = RegulatorySearchAgent()
        
        # Test the _search_regulatory_data method
        results = agent._search_regulatory_data("healthcare data protection")
        
        # Check that we got some results
        self.assertTrue(len(results) > 0, "Should return at least one result")
        
        # Test the _extract_sources_from_search method
        search_results = """
        HIPAA Compliance Guide: https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/index.html
        Data Protection in Healthcare: https://healthitsecurity.com/features/healthcare-data-security
        """
        
        extracted = agent._extract_sources_from_search(search_results)
        
        # Check that we extracted at least one source
        self.assertTrue(len(extracted) > 0, "Should extract at least one source")
    
    @unittest.skipIf(not AGENTS_AVAILABLE, "Regulatory agents not available")
    def test_search_with_agents(self):
        """Test the search_with_agents function."""
        # This test might take some time as it involves API calls
        results = search_with_agents("financial reporting requirements for public companies")
        
        # Check that we got some results
        self.assertTrue(len(results) > 0, "Should return at least one result")
        
        # Check that the results are sorted by relevance
        if len(results) > 1:
            self.assertGreaterEqual(
                results[0].get("relevance_score", 0), 
                results[1].get("relevance_score", 0),
                "Results should be sorted by relevance score"
            )

if __name__ == "__main__":
    unittest.main() 