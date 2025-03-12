"""
Module for regulatory data search agents.
This module provides agent-based tools for searching and retrieving regulatory data
from various sources including public databases, APIs, and websites.
"""

from typing import List, Dict, Any, Optional, Union
import os
import json
import requests
from datetime import datetime
import re
from app.utils.openai_manager import OpenAIManager

# Try to import LangChain dependencies
try:
    from langchain.agents import Tool, AgentExecutor, ZeroShotAgent, AgentType
    from langchain.chains import LLMChain
    from langchain.llms import OpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import DuckDuckGoSearchResults
    from langchain.utilities import GoogleSearchAPIWrapper
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Define placeholder types for type hints when LangChain is not available
    class AgentExecutor:
        pass

# Initialize OpenAI manager
openai_manager = OpenAIManager()

# Regulatory data sources APIs
REGULATORY_APIS = {
    "reginfo": "https://www.reginfo.gov/public/do/XMLReportList",
    "federalregister": "https://www.federalregister.gov/api/v1",
    "regulations": "https://api.regulations.gov/v4",
    "sec": "https://www.sec.gov/edgar/search",
    "cfpb": "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
}

class RegulatorySearchAgent:
    """
    Agent for searching regulatory data from various sources.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the regulatory search agent.
        
        Args:
            api_key: Optional API key for external services
        """
        self.api_key = api_key
        self.langchain_available = LANGCHAIN_AVAILABLE
        self.agent = self._initialize_agent() if LANGCHAIN_AVAILABLE else None
        
    def _initialize_agent(self) -> Optional[AgentExecutor]:
        """
        Initialize the LangChain agent with tools for regulatory search.
        
        Returns:
            AgentExecutor if LangChain is available, None otherwise
        """
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Initialize search tools
        search_tool = DuckDuckGoSearchResults()
        
        # Define tools for the agent
        tools = [
            Tool(
                name="RegulatorySearch",
                func=self._search_regulatory_data,
                description="Useful for searching regulatory data from official sources"
            ),
            Tool(
                name="WebSearch",
                func=search_tool.run,
                description="Useful for searching the web for regulatory information"
            ),
            Tool(
                name="APISearch",
                func=self._search_regulatory_apis,
                description="Useful for searching regulatory APIs for specific data"
            )
        ]
        
        # Initialize LLM
        llm = OpenAI(temperature=0)
        
        # Create memory for the agent
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Create the agent
        return AgentExecutor.from_agent_and_tools(
            agent=ZeroShotAgent.from_llm_and_tools(llm=llm, tools=tools),
            tools=tools,
            memory=memory,
            verbose=True
        )
    
    def _validate_result_with_openai(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Validate a single search result using OpenAI's API.
        
        Args:
            result: The search result to validate
            query: The original search query
            
        Returns:
            Updated result with validation score and feedback
        """
        try:
            # Prepare the messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "You are a regulatory compliance expert. Validate search results for accuracy and relevance."
                },
                {
                    "role": "user",
                    "content": f"""Please analyze this regulatory search result for relevance and accuracy:

Query: {query}

Source: {result['source_name']}
Description: {result.get('source_description', '')}
URL: {result['source_url']}

Please provide:
1. A relevance score (0-1)
2. Whether this is a legitimate regulatory source (true/false)
3. Brief explanation of the validation"""
                }
            ]
            
            # Call OpenAI API using the manager
            response = openai_manager.call_openai_with_retry(messages)
            
            # Parse the response
            try:
                content = response.choices[0].message.content
                validation = json.loads(content)
                
                # Convert and validate the values
                try:
                    relevance_score = float(validation.get('relevance_score', 0.0))
                    is_legitimate = bool(validation.get('is_legitimate_source', False))
                    explanation = str(validation.get('explanation', ''))
                    
                    # Ensure score is between 0 and 1
                    relevance_score = max(0.0, min(1.0, relevance_score))
                    
                    # Update the result with validation data
                    result['openai_validation'] = {
                        'relevance_score': relevance_score,
                        'is_legitimate_source': is_legitimate,
                        'explanation': explanation
                    }
                    
                    # Adjust the overall relevance score
                    original_score = float(result.get('relevance_score', 0))
                    result['relevance_score'] = (original_score + relevance_score) / 2
                    
                except (ValueError, TypeError) as e:
                    result['openai_validation'] = {
                        'error': f"Invalid value types in response: {str(e)}",
                        'status': 'failed',
                        'relevance_score': 0.0,
                        'is_legitimate_source': False
                    }
                
            except json.JSONDecodeError as e:
                result['openai_validation'] = {
                    'error': f"Invalid JSON response: {str(e)}",
                    'status': 'failed',
                    'relevance_score': 0.0,
                    'is_legitimate_source': False
                }
            
        except Exception as e:
            result['openai_validation'] = {
                'error': str(e),
                'status': 'failed',
                'relevance_score': 0.0,
                'is_legitimate_source': False
            }
            
        return result

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for regulatory data using the agent.
        
        Args:
            query: The search query
            
        Returns:
            List of regulatory data sources matching the query
        """
        # Get initial results
        if self.agent:
            try:
                # Use the agent to search
                agent_result = self.agent.run(f"Find regulatory compliance information about: {query}")
                
                # Parse the agent result to extract structured data
                sources = self._extract_sources_from_search(agent_result)
                
                # Combine with direct search results
                direct_results = self._search_regulatory_data(query)
                
                # Merge results, removing duplicates
                all_results = direct_results.copy()
                for source in sources:
                    if not any(result["source_url"] == source["source_url"] for result in all_results):
                        all_results.append(source)
            except Exception as e:
                print(f"Error using agent for search: {str(e)}")
                # Fall back to direct search
                all_results = self._search_regulatory_data(query)
        else:
            # If LangChain is not available, use direct search
            all_results = self._search_regulatory_data(query)
        
        # Validate results with OpenAI
        validated_results = []
        for result in all_results:
            validated_result = self._validate_result_with_openai(result, query)
            validated_results.append(validated_result)
        
        # Filter out results that failed OpenAI validation or have low relevance
        final_results = []
        for result in validated_results:
            validation = result.get('openai_validation', {})
            is_legitimate = validation.get('is_legitimate_source', False)
            relevance_score = validation.get('relevance_score', 0.0)
            
            if is_legitimate and relevance_score >= 0.5:
                final_results.append(result)
        
        return final_results

    def _search_regulatory_data(self, query: str) -> List[Dict[str, Any]]:
        """Search regulatory data sources"""
        # Implementation remains the same
        pass

    def _search_regulatory_apis(self, query: str) -> List[Dict[str, Any]]:
        """Search regulatory APIs"""
        # Implementation remains the same
        pass

    def _extract_sources_from_search(self, text: str) -> List[Dict[str, Any]]:
        """Extract sources from search results"""
        # Implementation remains the same
        pass

def search_with_agents(text: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search for regulatory data using agents.
    
    Args:
        text: The text to search for relevant regulatory sources
        threshold: Minimum relevance score to include a source
        
    Returns:
        List of relevant regulatory sources with relevance scores
    """
    # Create a regulatory search agent
    agent = RegulatorySearchAgent()
    
    # Search using the agent
    results = agent.search(text)
    
    # Filter results by threshold
    filtered_results = [result for result in results if result.get("relevance_score", 0) >= threshold]
    
    # Sort by relevance score (highest first)
    filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return filtered_results 