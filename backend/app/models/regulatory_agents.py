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
from duckduckgo_search import DDGS
from langchain_community.utilities import DuckDuckGoSearchRun
from langchain.agents import Tool, AgentExecutor, OpenAIFunctionsAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

# Try to import LangChain dependencies
try:
    from langchain_core.tools import Tool, BaseTool
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import SystemMessage, HumanMessage
    from langchain_openai import ChatOpenAI
    from langchain_community.tools import DuckDuckGoSearchResults
    from langchain_community.utilities import GoogleSearchAPIWrapper
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Error importing LangChain dependencies: {str(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
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
    def __init__(self):
        """Initialize the RegulatorySearchAgent."""
        print("Initializing RegulatorySearchAgent...")
        self.openai_manager = OpenAIManager()
        if not self.openai_manager.api_key:
            print("Warning: No OpenAI API key found")
        else:
            print("OpenAI API key found")
            
        try:
            self.agent = self._initialize_agent()
            if self.agent is None:
                print("Warning: Agent initialization failed")
            else:
                print("Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            self.agent = None

    def _initialize_agent(self) -> Optional[AgentExecutor]:
        """
        Initialize the LangChain agent with tools for regulatory search.
        
        Returns:
            AgentExecutor if LangChain is available, None otherwise
        """
        try:
            print("Initializing LangChain agent...")
            
            # Initialize search tools
            print("Initializing search tools...")
            tools = [
                Tool(
                    name="web_search",
                    func=self._web_search,
                    description="Search the web for additional information about cryptocurrency regulations."
                )
            ]
            
            print("Defining agent tools...")
            
            # Initialize OpenAI ChatModel
            print("Initializing OpenAI ChatModel...")
            llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0,
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Create memory
            print("Creating agent memory...")
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create agent prompt
            print("Creating agent prompt...")
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a regulatory analysis expert. Your task is to analyze the provided sources and extract key information about cryptocurrency regulations.

For each source:
1. Extract the title, date, and key points
2. Identify specific regulatory requirements
3. Note any compliance deadlines

Format your response as a JSON object with:
{{
  "sources": [
    {{
      "url": "source URL",
      "date": "publication date",
      "title": "source title",
      "key_points": ["list of key points"],
      "requirements": ["list of requirements"],
      "deadlines": ["list of deadlines"]
    }}
  ],
  "summary": "overview of findings"
}}

Do not apologize or ask for clarification - analyze what you have."""),
                ("human", "{input}"),
                ("ai", "{agent_scratchpad}")
            ])
            
            # Create OpenAI Tools agent
            print("Creating OpenAI tools agent...")
            agent = OpenAIFunctionsAgent(
                llm=llm,
                tools=tools,
                prompt=prompt
            )
            
            # Create AgentExecutor
            print("Creating AgentExecutor...")
            return AgentExecutor(
                agent=agent,
                tools=tools,
                memory=memory,
                max_iterations=3,
                early_stopping_method="force",
                verbose=True
            )
            
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            return None
    
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
            response = self.openai_manager.call_openai_with_retry(messages)
            
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
            List of validated search results
        """
        print(f"Searching for: {query}")
        
        if not self.agent:
            print("No agent available for search")
            return []
            
        try:
            # First, search regulatory databases
            print("Searching regulatory databases...")
            regulatory_results = self._search_regulatory_data(query)
            print(f"Found {len(regulatory_results)} results from regulatory databases")
            
            # Then, search APIs
            print("Searching regulatory APIs...")
            api_results = self._search_regulatory_apis(query)
            print(f"Found {len(api_results)} results from APIs")
            
            # Combine initial results
            all_results = regulatory_results + api_results
            
            # If we have results, use the agent to analyze them
            if all_results:
                print("Running agent for analysis...")
                agent_response = self.agent.invoke({
                    "input": f"""Here are the regulatory sources to analyze:
                    
                    {json.dumps(all_results, indent=2)}
                    
                    Please analyze these sources and extract key information about cryptocurrency regulations."""
                })
                
                print(f"Agent response received: {agent_response}")
                
                # Try to parse the agent's response
                if isinstance(agent_response, dict) and 'output' in agent_response:
                    try:
                        # Try to parse the output as JSON
                        agent_data = json.loads(agent_response['output'])
                        
                        # Return the agent's analysis directly
                        return agent_data.get('sources', [])
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing agent response as JSON: {str(e)}")
                        # Try to extract URLs from text response
                        web_results = self._extract_sources_from_search(agent_response['output'])
                        return web_results
            
            print(f"No results found")
            return []
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def _search_regulatory_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Search regulatory data sources directly.
        
        Args:
            query: The search query
            
        Returns:
            List of regulatory data sources
        """
        results = []
        
        try:
            # Search SEC EDGAR database using their public website search
            if "sec" in query.lower() or "securities" in query.lower():
                print("Searching SEC EDGAR database...")
                # Use DuckDuckGo to search SEC's website
                search_tool = DuckDuckGoSearchResults()
                sec_results = search_tool.run(f"site:sec.gov {query}")
                
                # Extract SEC URLs and context
                for result in self._extract_sources_from_search(sec_results):
                    if "sec.gov" in result["source_url"]:
                        result["source_name"] = "SEC EDGAR"
                        result["relevance_score"] = 0.8  # Higher score for SEC sources
                        results.append(result)
            
            # Search Federal Register
            print("Searching Federal Register...")
            try:
                response = requests.get(
                    f"{REGULATORY_APIS['federalregister']}/documents/search",
                    params={
                        "per_page": 20,
                        "order": "relevance",
                        "conditions[term]": query
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("results", []):
                        results.append({
                            "source_name": "Federal Register",
                            "source_url": item.get("html_url", ""),
                            "source_description": item.get("abstract", ""),
                            "relevance_score": 0.7,  # Default score since API doesn't provide one
                            "date": item.get("publication_date", "")
                        })
            except Exception as e:
                print(f"Error searching Federal Register: {str(e)}")
                # Fall back to DuckDuckGo search
                fr_results = search_tool.run(f"site:federalregister.gov {query}")
                results.extend(self._extract_sources_from_search(fr_results))
            
        except Exception as e:
            print(f"Error in direct regulatory search: {str(e)}")
        
        return results

    def _search_regulatory_apis(self, query: str) -> List[Dict[str, Any]]:
        """
        Search regulatory APIs for specific data.
        
        Args:
            query: The search query
            
        Returns:
            List of regulatory data from APIs
        """
        results = []
        search_tool = DuckDuckGoSearchResults()
        
        try:
            # Search Regulations.gov
            print("Searching Regulations.gov...")
            try:
                headers = {"X-Api-Key": os.getenv("REGULATIONS_GOV_API_KEY", "")}
                response = requests.get(
                    f"{REGULATORY_APIS['regulations']}/documents",
                    headers=headers,
                    params={
                        "filter[searchTerm]": query,
                        "sort": "relevance",
                        "page[size]": 20
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("data", []):
                        attributes = item.get("attributes", {})
                        results.append({
                            "source_name": "Regulations.gov",
                            "source_url": f"https://www.regulations.gov/document/{item.get('id', '')}",
                            "source_description": attributes.get("title", ""),
                            "relevance_score": 0.8,  # Default score since API doesn't provide one
                            "date": attributes.get("postedDate", "")
                        })
            except Exception as e:
                print(f"Error searching Regulations.gov: {str(e)}")
                # Fall back to DuckDuckGo search
                reg_results = search_tool.run(f"site:regulations.gov {query}")
                results.extend(self._extract_sources_from_search(reg_results))
            
            # Search CFPB Consumer Complaints
            if "consumer" in query.lower() or "financial" in query.lower():
                print("Searching CFPB database...")
                try:
                    response = requests.get(
                        REGULATORY_APIS["cfpb"],
                        params={
                            "search_term": query,
                            "size": 20
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("hits", {}).get("hits", []):
                            source = item.get("_source", {})
                            results.append({
                                "source_name": "CFPB Consumer Complaints",
                                "source_url": f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/{source.get('id', '')}",
                                "source_description": source.get("complaint_what_happened", ""),
                                "relevance_score": item.get("_score", 0) / 100,
                                "date": source.get("date_received", "")
                            })
                except Exception as e:
                    print(f"Error searching CFPB: {str(e)}")
                    # Fall back to DuckDuckGo search
                    cfpb_results = search_tool.run(f"site:consumerfinance.gov {query}")
                    results.extend(self._extract_sources_from_search(cfpb_results))
        
        except Exception as e:
            print(f"Error in API search: {str(e)}")
        
        return results

    def _extract_sources_from_search(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sources from search results text.
        
        Args:
            text: The text to extract sources from
            
        Returns:
            List of extracted sources
        """
        results = []
        
        try:
            # Look for URLs in the text
            urls = re.findall(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', text)
            
            # Extract text around each URL as context
            for url in urls:
                # Find the context around the URL
                url_index = text.find(url)
                start_index = max(0, url_index - 200)
                end_index = min(len(text), url_index + len(url) + 200)
                context = text[start_index:end_index]
                
                # Try to extract a title/description from the context
                lines = context.split('\n')
                description = next((line for line in lines if url not in line), context)
                
                # Determine the source name from the URL
                source_name = "Unknown Source"
                relevance_score = 0.5  # Default score
                
                if "sec.gov" in url:
                    source_name = "SEC"
                    relevance_score = 0.8
                elif "federalregister.gov" in url:
                    source_name = "Federal Register"
                    relevance_score = 0.7
                elif "regulations.gov" in url:
                    source_name = "Regulations.gov"
                    relevance_score = 0.7
                elif "consumerfinance.gov" in url:
                    source_name = "CFPB"
                    relevance_score = 0.7
                
                # Clean up the description
                description = description.strip()
                if len(description) > 500:
                    description = description[:497] + "..."
                
                results.append({
                    "source_name": source_name,
                    "source_url": url,
                    "source_description": description,
                    "relevance_score": relevance_score,
                    "date": datetime.now().strftime("%Y-%m-%d")  # Use current date as we don't have the actual date
                })
        
        except Exception as e:
            print(f"Error extracting sources from text: {str(e)}")
        
        return results

    def _web_search(self, query: str) -> str:
        """
        Search the web for regulatory information.
        
        Args:
            query: The search query
            
        Returns:
            String containing search results
        """
        try:
            # Use DuckDuckGo to search
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(f"site:sec.gov {query}", max_results=5):
                    results.append(f"{r['title']}: {r['body']} ({r['link']})")
                return "\n".join(results)
            
        except Exception as e:
            print(f"Error during web search: {str(e)}")
            return ""

def search_with_agents(text: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search for regulatory data using agents.
    
    Args:
        text: The text to search for relevant regulatory sources
        threshold: Minimum relevance score to include a source
        
    Returns:
        List of relevant regulatory sources with relevance scores
    """
    print("Starting agent-based search...")
    try:
        # Create a regulatory search agent
        print("Initializing RegulatorySearchAgent...")
        agent = RegulatorySearchAgent()
        
        if agent.agent is None:
            print("Warning: LangChain agent initialization failed")
            return []
            
        # Search using the agent
        print("Performing search with agent...")
        results = agent.search(text)
        
        if results is None:
            print("Warning: Agent search returned None")
            return []
            
        print(f"Found {len(results)} initial results")
        
        # Filter results by threshold
        filtered_results = [result for result in results if result.get("relevance_score", 0) >= threshold]
        
        print(f"Filtered to {len(filtered_results)} results above threshold {threshold}")
        
        # Sort by relevance score (highest first)
        filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return filtered_results
        
    except Exception as e:
        print(f"Error in agent-based search: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return [] 