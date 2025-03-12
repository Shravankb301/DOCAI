"""
Tests for the regulatory data search agents.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from typing import Dict, Any, List

from .regulatory_agents import RegulatorySearchAgent, REGULATORY_APIS

class TestRegulatorySearchAgent(unittest.TestCase):
    """Test cases for RegulatorySearchAgent"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = "test_api_key"
        self.agent = RegulatorySearchAgent(api_key=self.api_key)
        
        # Sample test data
        self.sample_result = {
            "source_name": "Federal Register - Regulatory Guidelines",
            "source_url": "https://www.federalregister.gov/documents/test",
            "source_description": "Guidelines for financial compliance",
            "relevance_score": 0.8,
            "matched_categories": ["regulatory", "compliance"]
        }
        
        # Mock OpenAI validation response
        self.mock_openai_response = {
            "relevance_score": 0.9,
            "is_legitimate_source": True,
            "explanation": "This is a legitimate government source with relevant content."
        }

    @patch('openai.ChatCompletion.create')
    def test_openai_mock_response(self, mock_openai):
        """Test basic OpenAI API mocking and response handling"""
        # Create a test result
        test_result = {
            "source_name": "Test Source",
            "source_url": "https://test.gov",
            "source_description": "Test description",
            "relevance_score": 0.7
        }

        # Create a mock OpenAI response
        mock_validation = {
            "relevance_score": 0.8,
            "is_legitimate_source": True,
            "explanation": "Valid test source"
        }

        # Setup the mock
        mock_response = type('MockResponse', (), {
            'choices': [
                type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': json.dumps(mock_validation)
                    })
                })
            ]
        })
        mock_openai.return_value = mock_response

        # Test the validation
        print("\nTesting OpenAI mock response:")
        validated_result = self.agent._validate_result_with_openai(test_result, "test query")
        print(f"Input result: {test_result}")
        print(f"Mock OpenAI response content: {mock_validation}")
        print(f"Validated result: {validated_result}")

        # Assertions
        self.assertIn('openai_validation', validated_result)
        self.assertEqual(validated_result['openai_validation']['is_legitimate_source'], True)
        self.assertEqual(validated_result['openai_validation']['relevance_score'], 0.8)
        self.assertEqual(validated_result['openai_validation']['explanation'], "Valid test source")
        # Check that the overall relevance score is updated (average of original and validation scores)
        self.assertAlmostEqual(validated_result['relevance_score'], 0.75)  # (0.7 + 0.8) / 2

    @patch('openai.ChatCompletion.create')
    def test_validate_result_with_openai(self, mock_openai):
        """Test OpenAI validation of search results"""
        # Setup mock response
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content=json.dumps(self.mock_openai_response),
                    model_dump=lambda: {"content": json.dumps(self.mock_openai_response)}
                )
            )]
        )
        
        # Test validation
        validated_result = self.agent._validate_result_with_openai(self.sample_result, "financial regulations")
        
        # Assertions
        self.assertIn('openai_validation', validated_result)
        self.assertEqual(validated_result['openai_validation']['is_legitimate_source'], True)
        self.assertAlmostEqual(validated_result['relevance_score'], 0.85)  # Average of 0.8 and 0.9

    @patch('requests.get')
    def test_search_regulatory_apis(self, mock_get):
        """Test searching regulatory APIs"""
        # Mock API response
        mock_api_response = {
            "results": [{
                "title": "Test Regulation",
                "html_url": "https://test.gov/regulation",
                "abstract": "Test description",
                "publication_date": "2024-01-01",
                "agencies": [{"name": "Test Agency"}],
                "type": "Rule"
            }]
        }
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_api_response
        )
        
        # Test API search
        results = self.agent._search_regulatory_apis("test query")
        
        # Assertions
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['source_name'], "Test Regulation")

    def test_extract_sources_from_search(self):
        """Test extraction of sources from search results"""
        test_search_results = """
        Important regulation from gov site. https://www.regulations.gov/document/test
        Another source from https://www.compliance.law/guidelines
        Invalid source from https://example.com/test
        """
        
        sources = self.agent._extract_sources_from_search(test_search_results)
        
        # Assertions
        self.assertEqual(len(sources), 2)  # Should only extract regulatory sources
        self.assertTrue(all('gov' in s['source_url'] or 'law' in s['source_url'] for s in sources))

    @patch('openai.ChatCompletion.create')
    def test_search_with_invalid_results(self, mock_openai):
        """Test search with results that fail validation"""
        # Mock OpenAI to reject the source
        invalid_response = {
            "relevance_score": 0.2,
            "is_legitimate_source": False,
            "explanation": "Not a legitimate regulatory source"
        }
        
        # Create a proper mock response
        mock_response = type('MockResponse', (), {
            'choices': [
                type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': json.dumps(invalid_response)
                    })
                })
            ]
        })
        mock_openai.return_value = mock_response
        
        with patch.object(self.agent, '_search_regulatory_data') as mock_search:
            mock_search.return_value = [self.sample_result]
            
            # Add debug logging
            print("\nTesting invalid results:")
            print(f"Mock OpenAI response: {invalid_response}")
            results = self.agent.search("test query")
            print(f"Results after search: {results}")
            print(f"First result validation: {results[0].get('openai_validation', {}) if results else 'No results'}")
            
            # Should filter out invalid results
            self.assertEqual(len(results), 0)

    def test_error_handling(self):
        """Test error handling in search process"""
        # Test with invalid API key
        agent = RegulatorySearchAgent(api_key="invalid_key")
        results = agent.search("test query")
        
        # Should fall back to direct search
        self.assertIsInstance(results, list)

    @patch('openai.ChatCompletion.create')
    def test_batch_validation(self, mock_openai):
        """Test validation of multiple results"""
        # Create multiple test results
        test_results = [
            {
                "source_name": f"Test Source {i}",
                "source_url": f"https://test{i}.gov",
                "source_description": f"Test description {i}",
                "relevance_score": 0.8
            }
            for i in range(3)
        ]
        
        # Mock OpenAI to alternate between valid and invalid results
        mock_responses = [
            {"relevance_score": 0.9, "is_legitimate_source": True, "explanation": "Valid"},
            {"relevance_score": 0.2, "is_legitimate_source": False, "explanation": "Invalid"},
            {"relevance_score": 0.8, "is_legitimate_source": True, "explanation": "Valid"}
        ]
        
        # Create proper mock responses
        mock_responses_iter = iter(mock_responses)  # Create an iterator for responses
        def mock_openai_side_effect(*args, **kwargs):
            response = next(mock_responses_iter)
            return type('MockResponse', (), {
                'choices': [
                    type('MockChoice', (), {
                        'message': type('MockMessage', (), {
                            'content': json.dumps(response)
                        })
                    })
                ]
            })
        mock_openai.side_effect = mock_openai_side_effect
        
        with patch.object(self.agent, '_search_regulatory_data') as mock_search:
            mock_search.return_value = test_results
            
            # Add debug logging
            print("\nTesting batch validation:")
            print(f"Mock OpenAI responses: {mock_responses}")
            results = self.agent.search("test query")
            print(f"Number of results: {len(results)}")
            for i, result in enumerate(results):
                print(f"\nResult {i}:")
                print(f"OpenAI validation: {result.get('openai_validation', {})}")
                print(f"Relevance score: {result.get('relevance_score')}")
            
            # Should only return valid results
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r.get('openai_validation', {}).get('is_legitimate_source', False) for r in results))
            self.assertTrue(all(r.get('openai_validation', {}).get('relevance_score', 0) >= 0.5 for r in results))

    def test_api_integration(self):
        """Test integration with regulatory APIs"""
        for api_name, api_url in REGULATORY_APIS.items():
            with patch('requests.get') as mock_get:
                mock_get.return_value = MagicMock(
                    status_code=200,
                    json=lambda: {"results": []}
                )
                
                # Test each API endpoint
                results = self.agent._search_regulatory_apis(f"test query for {api_name}")
                
                # Should handle the API response without errors
                self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main() 