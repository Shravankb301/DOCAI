import re
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.utils.openai_manager import OpenAIManager
from duckduckgo_search import DDGS
from langchain.agents import Tool, AgentExecutor, OpenAIFunctionsAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

class RegulatorySearchAgent:
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

    def _initialize_agent(self) -> Optional[AgentExecutor]:
        """
        Initialize the agent with tools and prompt.
        
        Returns:
            AgentExecutor if successful, None otherwise
        """
        try:
            # Initialize search tools
            tools = [
                Tool(
                    name="regulatory_search",
                    func=self._search_regulatory_data,
                    description="Search regulatory databases for information about regulations. Returns a list of regulatory documents with source_name, source_url, source_description, and date."
                ),
                Tool(
                    name="api_search",
                    func=self._search_regulatory_apis,
                    description="Search regulatory APIs for information about regulations. Returns a list of regulatory documents with source_name, source_url, source_description, and date."
                )
            ]
            
            # Initialize the model
            llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0,
                api_key=self.openai_manager.api_key
            )
            
            # Create memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create prompt template
            template = """You are a regulatory search agent specializing in finding and analyzing regulatory information.

When searching for regulatory information:
1. First use the regulatory_search tool to find relevant documents from regulatory databases
2. Then use the api_search tool to find additional information from regulatory APIs
3. Analyze all results to extract key points, requirements, and deadlines
4. Format your response as a JSON object with the following structure:
{
    "sources": [
        {
            "title": "Document title",
            "url": "Source URL",
            "key_points": ["List of key points"],
            "requirements": ["List of requirements"],
            "deadlines": ["List of deadlines if any"],
            "relevance": "High/Medium/Low"
        }
    ],
    "summary": "A concise summary of the findings"
}

IMPORTANT:
- Your response MUST be a valid JSON object
- Do not include any text before or after the JSON
- Do not include markdown code blocks
- If you find no results, return an empty sources list and appropriate summary
- Always include both sources and summary keys
- Format dates as YYYY-MM-DD
- Use "High", "Medium", or "Low" for relevance
- For each source:
  - Extract title from source_description or source_name
  - Use source_url for the URL
  - Analyze source_description to identify key points
  - Look for requirements and deadlines in the description
  - Set relevance based on source_name and content relevance

Previous conversation:
{chat_history}"""

            # Create the agent
            agent = OpenAIFunctionsAgent.from_llm_and_tools(
                llm=llm,
                tools=tools,
                system_message=template
            )
            
            # Create the executor
            return AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=tools,
                memory=memory,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
            
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            return None

    def search(self, query: str) -> Dict[str, Any]:
        """
        Search for regulatory information using the agent.
        
        Args:
            query: The search query
            
        Returns:
            Dict containing search results and analysis
        """
        try:
            if not self.agent:
                print("Error: Agent not initialized")
                return {
                    "sources": [],
                    "summary": "Error: Agent not initialized",
                    "error": True
                }
                
            # First search regulatory databases
            print("Searching regulatory databases...")
            db_results = self._search_regulatory_data(query)
            print(f"Found {len(db_results)} results from regulatory databases")
            
            # Then search regulatory APIs
            print("Searching regulatory APIs...")
            api_results = self._search_regulatory_apis(query)
            print(f"Found {len(api_results)} results from regulatory APIs")
            
            # Combine results
            all_results = db_results + api_results
            if not all_results:
                return {
                    "sources": [],
                    "summary": "No relevant regulatory information found.",
                    "error": False
                }
                
            # Have the agent analyze the results
            analysis_prompt = f"""Analyze these regulatory sources about {query}:
            
            Sources:
            {json.dumps(all_results, indent=2)}
            
            Extract key points, requirements, and deadlines from each source.
            Format your response as specified in the system prompt.
            Remember to return ONLY a valid JSON object with no additional text."""
            
            # Run the agent with retries
            max_retries = 3
            retry_delay = 2
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    # Run the agent
                    response = self.agent.run(analysis_prompt)
                    
                    # Parse the response
                    if isinstance(response, str):
                        # Try to find JSON in the response
                        json_start = response.find('{')
                        json_end = response.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = response[json_start:json_end]
                            try:
                                # Try to parse as is
                                results = json.loads(json_str)
                            except json.JSONDecodeError:
                                # Clean up the JSON string
                                json_str = re.sub(r'```json\s*|\s*```', '', json_str)
                                json_str = re.sub(r'\\n', '', json_str)
                                json_str = re.sub(r'\\', '', json_str)
                                results = json.loads(json_str)
                        else:
                            raise ValueError("No JSON found in response")
                    else:
                        results = response
                        
                    # Validate the structure
                    if not isinstance(results, dict):
                        raise ValueError("Response is not a dictionary")
                    if "sources" not in results:
                        raise ValueError("Response missing 'sources' key")
                    if "summary" not in results:
                        raise ValueError("Response missing 'summary' key")
                        
                    # Add error status
                    results["error"] = False
                    return results
                    
                except Exception as e:
                    last_error = str(e)
                    print(f"Attempt {attempt + 1} failed: {last_error}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print("All retry attempts failed")
                
            # If we get here, all retries failed
            print(f"Failed to parse agent response after {max_retries} attempts")
            if isinstance(response, str):
                # Try to extract useful information from the text response
                return {
                    "sources": [
                        {
                            "title": "Agent Analysis",
                            "url": "",
                            "key_points": [response],
                            "requirements": [],
                            "deadlines": [],
                            "relevance": "Medium"
                        }
                    ],
                    "summary": response,
                    "error": True,
                    "error_message": last_error
                }
            else:
                return {
                    "sources": [],
                    "summary": "Failed to analyze regulatory information",
                    "error": True,
                    "error_message": last_error
                }
                
        except Exception as e:
            error_message = str(e)
            print(f"Error during search: {error_message}")
            return {
                "sources": [],
                "summary": "Error during regulatory search",
                "error": True,
                "error_message": error_message
            }

    def _search_regulatory_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Search regulatory databases for information.
        
        Args:
            query: The search query
            
        Returns:
            List of search results
        """
        try:
            # Search SEC EDGAR database
            print("Searching SEC EDGAR database...")
            results = []
            
            # Use web search to find SEC documents with retry logic
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    with DDGS() as ddgs:
                        # First try SEC-specific search
                        sec_query = f"site:sec.gov/edgar {query}"
                        found_results = False
                        
                        for r in ddgs.text(sec_query, max_results=3):
                            # Extract fields with proper fallbacks
                            title = r.get('title', '').strip()
                            body = r.get('body', '').strip()
                            link = r.get('link', '').strip()
                            
                            # Skip if no link or if not from SEC
                            if not link or 'sec.gov' not in link:
                                continue
                                
                            # Clean up the title
                            title = re.sub(r'\s+', ' ', title)
                            if len(title) > 100:
                                title = title[:97] + "..."
                                
                            # Clean up the body
                            body = re.sub(r'\s+', ' ', body)
                            if len(body) > 500:
                                body = body[:497] + "..."
                                
                            results.append({
                                "source_name": "SEC EDGAR",
                                "source_url": link,
                                "source_description": f"{title}\n\nExcerpt: {body}",
                                "relevance_score": 0.9 if 'edgar' in link.lower() else 0.8,
                                "date": datetime.now().strftime('%Y-%m-%d')
                            })
                            found_results = True
                            
                            # Add a small delay between results
                            time.sleep(0.5)
                            
                        # If no EDGAR results, try general SEC search
                        if not found_results:
                            sec_query = f"site:sec.gov {query}"
                            for r in ddgs.text(sec_query, max_results=5):
                                # Extract and clean fields
                                title = r.get('title', '').strip()
                                body = r.get('body', '').strip()
                                link = r.get('link', '').strip()
                                
                                # Skip if no link or if not from SEC
                                if not link or 'sec.gov' not in link:
                                    continue
                                    
                                # Clean up the title
                                title = re.sub(r'\s+', ' ', title)
                                if len(title) > 100:
                                    title = title[:97] + "..."
                                    
                                # Clean up the body
                                body = re.sub(r'\s+', ' ', body)
                                if len(body) > 500:
                                    body = body[:497] + "..."
                                    
                                results.append({
                                    "source_name": "SEC Website",
                                    "source_url": link,
                                    "source_description": f"{title}\n\nExcerpt: {body}",
                                    "relevance_score": 0.7,
                                    "date": datetime.now().strftime('%Y-%m-%d')
                                })
                                
                                # Add a small delay between results
                                time.sleep(0.5)
                    
                    # If we got here, the search was successful
                    break
                    
                except Exception as e:
                    print(f"Search attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("All retry attempts failed")
            
            # Search Federal Register
            print("Searching Federal Register...")
            try:
                fr_query = f"site:federalregister.gov {query}"
                with DDGS() as ddgs:
                    for r in ddgs.text(fr_query, max_results=3):
                        # Extract and clean fields
                        title = r.get('title', '').strip()
                        body = r.get('body', '').strip()
                        link = r.get('link', '').strip()
                        
                        # Skip if no link or if not from Federal Register
                        if not link or 'federalregister.gov' not in link:
                            continue
                            
                        # Clean up the title
                        title = re.sub(r'\s+', ' ', title)
                        if len(title) > 100:
                            title = title[:97] + "..."
                            
                        # Clean up the body
                        body = re.sub(r'\s+', ' ', body)
                        if len(body) > 500:
                            body = body[:497] + "..."
                            
                        results.append({
                            "source_name": "Federal Register",
                            "source_url": link,
                            "source_description": f"{title}\n\nExcerpt: {body}",
                            "relevance_score": 0.75,
                            "date": datetime.now().strftime('%Y-%m-%d')
                        })
                        
                        # Add a small delay between results
                        time.sleep(0.5)
                        
            except Exception as e:
                print(f"Error searching Federal Register: {str(e)}")
            
            return results
            
        except Exception as e:
            print(f"Error searching regulatory data: {str(e)}")
            return []

    def _search_regulatory_apis(self, query: str) -> List[Dict[str, Any]]:
        """
        Search regulatory APIs for information.
        
        Args:
            query: The search query
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            # Search Regulations.gov API
            print("Searching Regulations.gov...")
            # TODO: Implement Regulations.gov API search
            # For now, return empty results since we need API key
            
            return results
            
        except Exception as e:
            print(f"Error searching regulatory APIs: {str(e)}")
            return []

    def _extract_sources_from_search(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract source URLs from search results text.
        
        Args:
            text: The text to extract URLs from
            
        Returns:
            List of extracted sources
        """
        try:
            results = []
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
            
            for url in urls:
                if "sec.gov" in url:
                    results.append({
                        "source_name": "SEC",
                        "source_url": url,
                        "source_description": "Found in search results",
                        "relevance_score": 0.6,
                        "date": datetime.now().strftime('%Y-%m-%d')
                    })
            
            return results
            
        except Exception as e:
            print(f"Error extracting sources: {str(e)}")
            return [] 