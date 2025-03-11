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
        agent_chain = ZeroShotAgent.from_llm_and_tools(
            llm=llm,
            tools=tools,
            verbose=True
        )
        
        # Create the agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent_chain,
            tools=tools,
            verbose=True,
            memory=memory
        )
        
        return agent_executor
    
    def _search_regulatory_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for regulatory data based on the query.
        
        Args:
            query: The search query
            
        Returns:
            List of regulatory data sources matching the query
        """
        # Implement basic keyword matching for now
        from app.models.public_data import search_regulatory_sources
        
        # Use the existing search function
        results = search_regulatory_sources(query, threshold=0.2)
        
        # If no results, try to find more through web search
        if not results and LANGCHAIN_AVAILABLE:
            search_tool = DuckDuckGoSearchResults()
            search_results = search_tool.run(f"regulatory compliance {query}")
            
            # Extract potential regulatory sources from search results
            extracted_sources = self._extract_sources_from_search(search_results)
            results.extend(extracted_sources)
        
        return results
    
    def _search_regulatory_apis(self, query: str) -> List[Dict[str, Any]]:
        """
        Search regulatory APIs for data related to the query.
        
        Args:
            query: The search query
            
        Returns:
            List of results from regulatory APIs
        """
        results = []
        
        # Search Federal Register API
        try:
            # Example: Search Federal Register API
            fr_response = requests.get(
                f"{REGULATORY_APIS['federalregister']}/documents.json",
                params={"per_page": 5, "order": "relevance", "conditions[term]": query},
                timeout=10
            )
            
            if fr_response.status_code == 200:
                fr_data = fr_response.json()
                for item in fr_data.get("results", []):
                    results.append({
                        "source_name": item.get("title", ""),
                        "source_url": item.get("html_url", ""),
                        "source_description": item.get("abstract", ""),
                        "relevance_score": 0.8,  # Placeholder score
                        "publication_date": item.get("publication_date", ""),
                        "agency": item.get("agencies", [{}])[0].get("name", "") if item.get("agencies") else "",
                        "document_type": item.get("type", "")
                    })
        except Exception as e:
            print(f"Error searching Federal Register API: {str(e)}")
        
        return results
    
    def _extract_sources_from_search(self, search_results: str) -> List[Dict[str, Any]]:
        """
        Extract potential regulatory sources from search results.
        
        Args:
            search_results: The search results text
            
        Returns:
            List of extracted regulatory sources
        """
        sources = []
        
        # Look for URLs and titles in search results
        url_pattern = r'https?://(?:www\.)?([^\s/]+)([^\s]*)'
        urls = re.findall(url_pattern, search_results)
        
        for domain, path in urls:
            # Check if the domain is likely a regulatory source
            if any(keyword in domain for keyword in ["gov", "regulation", "compliance", "legal", "law"]):
                # Extract a title (text before the URL)
                title_match = re.search(r'([^.!?]*)[.!?]\s*https?://(?:www\.)?' + re.escape(domain), search_results)
                title = title_match.group(1).strip() if title_match else f"Regulatory source from {domain}"
                
                # Create a source entry
                sources.append({
                    "source_name": title,
                    "source_url": f"https://{domain}{path}",
                    "source_description": f"Regulatory information from {domain}",
                    "relevance_score": 0.6,  # Lower confidence for extracted sources
                    "matched_categories": ["regulatory", "compliance"]
                })
        
        return sources
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for regulatory data using the agent.
        
        Args:
            query: The search query
            
        Returns:
            List of regulatory data sources matching the query
        """
        if self.agent:
            try:
                # Use the agent to search
                agent_result = self.agent.run(f"Find regulatory compliance information about: {query}")
                
                # Parse the agent result to extract structured data
                # This is a simplified approach; in practice, you'd want more robust parsing
                sources = self._extract_sources_from_search(agent_result)
                
                # Combine with direct search results
                direct_results = self._search_regulatory_data(query)
                
                # Merge results, removing duplicates
                all_results = direct_results.copy()
                for source in sources:
                    if not any(result["source_url"] == source["source_url"] for result in all_results):
                        all_results.append(source)
                
                return all_results
            except Exception as e:
                print(f"Error using agent for search: {str(e)}")
                # Fall back to direct search
                return self._search_regulatory_data(query)
        else:
            # If LangChain is not available, use direct search
            return self._search_regulatory_data(query)

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