"""
OpenAI API manager module.
Provides utilities for managing OpenAI API interactions, including Assistants API integration.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential
import openai
from openai import OpenAI
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIManager:
    """Manager class for OpenAI API interactions"""
    
    def __init__(self, api_key: Optional[str] = None, max_daily_tokens: Optional[int] = None):
        """
        Initialize the OpenAI manager.
        
        Args:
            api_key: Optional API key. If not provided, will try to get from environment
            max_daily_tokens: Maximum tokens to use per day. If not provided, will try to get from environment
        """
        # Load API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or provide api_key parameter."
            )
        
        if not self._validate_api_key(self.api_key):
            raise ValueError(
                "Invalid OpenAI API key format. Key should start with 'sk-' and be at least "
                "40 characters long. Please check your API key."
            )
            
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize token budget
        self.max_daily_tokens = max_daily_tokens or int(os.getenv('OPENAI_MAX_TOKENS', '100000'))
        self.token_budget = TokenBudget(self.max_daily_tokens)
        
        # Initialize model configurations
        self.default_model = os.getenv('OPENAI_DEFAULT_MODEL', 'gpt-4')
        self.models = [
            {"name": "gpt-4", "max_tokens": 8192},
            {"name": "gpt-3.5-turbo", "max_tokens": 4096},
        ]
        
        # Create regulatory compliance assistant
        self.compliance_assistant = self._create_compliance_assistant()
        
        print(f"OpenAI Manager initialized successfully with model: {self.default_model}")
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate OpenAI API key format.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            bool: True if key format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        if not api_key.startswith('sk-'):
            return False
        if len(api_key) < 40:
            return False
        return True
    
    def _create_compliance_assistant(self) -> Any:
        """Create or get the regulatory compliance assistant"""
        try:
            # Create a new assistant for regulatory compliance
            assistant = self.client.beta.assistants.create(
                name="Regulatory Compliance Assistant",
                instructions="""You are a regulatory compliance expert. 
                Analyze documents and provide compliance assessments.
                Be thorough in your analysis and cite specific regulations when relevant.""",
                model="gpt-4",
                tools=[
                    {"type": "code_interpreter"},
                    {"type": "function", "function": {
                        "name": "search_regulations",
                        "description": "Search for relevant regulatory information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query for regulatory information"
                                }
                            },
                            "required": ["query"]
                        }
                    }}
                ]
            )
            return assistant
        except Exception as e:
            print(f"Error creating assistant: {str(e)}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call_openai_with_retry(self, messages: List[Dict[str, str]], 
                             max_tokens: int = 1000,
                             temperature: float = 0.3) -> Any:
        """
        Make an OpenAI API call with retry logic.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            
        Returns:
            OpenAI API response
        """
        try:
            # Estimate tokens
            estimated_tokens = self._estimate_tokens(str(messages))
            
            # Check token budget
            if not self.token_budget.can_use_tokens(estimated_tokens):
                raise Exception("Daily token budget exceeded")
            
            # Get appropriate model
            model = self._get_appropriate_model(estimated_tokens)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30
            )
            
            # Update token budget
            self.token_budget.add_used_tokens(
                response.usage.total_tokens if hasattr(response, 'usage') else estimated_tokens
            )
            
            return response
            
        except openai.RateLimitError:
            print("Rate limit reached, waiting...")
            time.sleep(20)
            raise
        except openai.APIError as e:
            if "insufficient_quota" in str(e):
                raise QuotaExceededError("OpenAI API quota exceeded") from e
            raise
    
    def analyze_compliance(self, text: str, regulations: List[str]) -> Dict[str, Any]:
        """
        Analyze text for regulatory compliance using the Assistants API.
        
        Args:
            text: Text to analyze
            regulations: List of relevant regulations
            
        Returns:
            Analysis results
        """
        try:
            # Create a new thread
            thread = self.client.beta.threads.create()
            
            # Add the message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Please analyze this text for compliance with the following regulations:
                {', '.join(regulations)}
                
                Text to analyze:
                {text}"""
            )
            
            # Run the analysis
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.compliance_assistant.id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                time.sleep(1)
            
            # Get the response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc"
            )
            
            # Extract the analysis
            analysis = messages.data[0].content[0].text.value
            
            return {
                "status": "success",
                "analysis": analysis,
                "thread_id": thread.id,
                "run_id": run.id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        # Rough estimation: 4 chars per token
        return len(text) // 4
    
    def _get_appropriate_model(self, estimated_tokens: int) -> str:
        """Get appropriate model based on token count"""
        for model in self.models:
            if estimated_tokens <= model["max_tokens"]:
                return model["name"]
        raise ValueError("Text too long for available models")


class TokenBudget:
    """Class to manage token usage budget"""
    
    def __init__(self, max_daily_tokens: int = 100000):
        """
        Initialize token budget tracker.
        
        Args:
            max_daily_tokens: Maximum tokens to use per day
        """
        self.max_daily_tokens = max_daily_tokens
        self.used_tokens = 0
        self.reset_time = datetime.now() + timedelta(days=1)
    
    def can_use_tokens(self, estimated_tokens: int) -> bool:
        """Check if we can use the estimated number of tokens"""
        if datetime.now() > self.reset_time:
            self.used_tokens = 0
            self.reset_time = datetime.now() + timedelta(days=1)
        return (self.used_tokens + estimated_tokens) <= self.max_daily_tokens
    
    def add_used_tokens(self, tokens: int):
        """Add used tokens to the count"""
        self.used_tokens += tokens


class QuotaExceededError(Exception):
    """Exception raised when API quota is exceeded"""
    pass 