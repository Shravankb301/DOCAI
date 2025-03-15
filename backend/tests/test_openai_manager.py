"""
Tests for the OpenAI manager module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime, timedelta
from app.utils.openai_manager import OpenAIManager, TokenBudget, QuotaExceededError

class TestOpenAIManager(unittest.TestCase):
    """Test cases for OpenAIManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = "sk-test123456789"
        self.manager = OpenAIManager(api_key=self.api_key)
        
        # Sample test data
        self.test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        # Mock OpenAI response
        self.mock_openai_response = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="Hello! How can I help you today?"
                    )
                )
            ],
            usage=MagicMock(
                total_tokens=50
            )
        )

    def test_validate_api_key(self):
        """Test API key validation"""
        # Valid key
        self.assertTrue(self.manager._validate_api_key("sk-test123456789012345678901234567890"))
        
        # Invalid keys
        self.assertFalse(self.manager._validate_api_key(""))
        self.assertFalse(self.manager._validate_api_key("invalid-key"))
        self.assertFalse(self.manager._validate_api_key("sk-short"))

    @patch('openai.OpenAI')
    def test_call_openai_with_retry(self, mock_openai):
        """Test OpenAI API call with retry logic"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self.mock_openai_response
        mock_openai.return_value = mock_client
        
        # Test successful call
        response = self.manager.call_openai_with_retry(self.test_messages)
        self.assertEqual(
            response.choices[0].message.content,
            "Hello! How can I help you today?"
        )
        
        # Test rate limit handling
        mock_client.chat.completions.create.side_effect = [
            openai.RateLimitError("Rate limit exceeded"),
            self.mock_openai_response
        ]
        response = self.manager.call_openai_with_retry(self.test_messages)
        self.assertEqual(
            response.choices[0].message.content,
            "Hello! How can I help you today?"
        )
        
        # Test quota exceeded
        mock_client.chat.completions.create.side_effect = openai.APIError("insufficient_quota")
        with self.assertRaises(QuotaExceededError):
            self.manager.call_openai_with_retry(self.test_messages)

    def test_token_budget(self):
        """Test token budget management"""
        budget = TokenBudget(max_daily_tokens=1000)
        
        # Test initial state
        self.assertTrue(budget.can_use_tokens(500))
        budget.add_used_tokens(500)
        
        # Test near limit
        self.assertTrue(budget.can_use_tokens(400))
        self.assertFalse(budget.can_use_tokens(600))
        
        # Test reset
        budget.reset_time = datetime.now() - timedelta(days=1)
        self.assertTrue(budget.can_use_tokens(1000))

    @patch('openai.OpenAI')
    def test_create_compliance_assistant(self, mock_openai):
        """Test compliance assistant creation"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.beta.assistants.create.return_value = MagicMock(id="asst_123")
        mock_openai.return_value = mock_client
        
        # Create new manager to test assistant creation
        manager = OpenAIManager(api_key=self.api_key)
        
        # Verify assistant was created
        self.assertIsNotNone(manager.compliance_assistant)
        mock_client.beta.assistants.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_analyze_compliance(self, mock_openai):
        """Test compliance analysis"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.beta.threads.create.return_value = MagicMock(id="thread_123")
        mock_client.beta.threads.runs.create.return_value = MagicMock(id="run_123")
        mock_client.beta.threads.runs.retrieve.return_value = MagicMock(status="completed")
        mock_client.beta.threads.messages.list.return_value = MagicMock(
            data=[
                MagicMock(
                    content=[
                        MagicMock(
                            text=MagicMock(
                                value="Compliance analysis complete. Document is compliant."
                            )
                        )
                    ]
                )
            ]
        )
        mock_openai.return_value = mock_client
        
        # Test analysis
        result = self.manager.analyze_compliance(
            "Sample document text",
            ["GDPR", "HIPAA"]
        )
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("analysis", result)
        self.assertIn("thread_id", result)
        self.assertIn("run_id", result)

    def test_estimate_tokens(self):
        """Test token estimation"""
        text = "This is a test message"  # 5 words, ~20 characters
        estimated_tokens = self.manager._estimate_tokens(text)
        self.assertEqual(estimated_tokens, 5)  # ~20/4 = 5

    def test_get_appropriate_model(self):
        """Test model selection based on token count"""
        # Test small text
        model = self.manager._get_appropriate_model(1000)
        self.assertEqual(model, "gpt-4")
        
        # Test medium text
        model = self.manager._get_appropriate_model(5000)
        self.assertEqual(model, "gpt-4")
        
        # Test large text
        with self.assertRaises(ValueError):
            self.manager._get_appropriate_model(10000)

if __name__ == '__main__':
    unittest.main() 