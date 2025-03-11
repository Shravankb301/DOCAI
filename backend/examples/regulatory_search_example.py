"""
Example script demonstrating how to use the regulatory search agents.
"""

import sys
import os
import json
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
    print("Warning: Regulatory agents not available. Make sure you have installed the required dependencies.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

def print_results(results: List[Dict[str, Any]], title: str) -> None:
    """
    Print the search results in a readable format.
    
    Args:
        results: The search results to print
        title: The title to display
    """
    print("\n" + "=" * 80)
    print(f"{title} ({len(results)} results)")
    print("=" * 80)
    
    for i, result in enumerate(results):
        print(f"\n[{i+1}] {result['source_name']}")
        print(f"    URL: {result['source_url']}")
        print(f"    Description: {result['source_description']}")
        print(f"    Relevance: {result['relevance_score']:.2f}")
        if "matched_categories" in result and result["matched_categories"]:
            print(f"    Categories: {', '.join(result['matched_categories'])}")

def main() -> None:
    """
    Main function to demonstrate the regulatory search agents.
    """
    # Example queries
    queries = [
        "data privacy and GDPR compliance",
        "financial reporting requirements for public companies",
        "healthcare data protection and HIPAA",
        "anti-money laundering regulations",
        "environmental compliance for manufacturing"
    ]
    
    print("\nRegulatory Search Example")
    print("========================\n")
    
    # Ask the user to select a query or enter their own
    print("Select a query or enter your own:")
    for i, query in enumerate(queries):
        print(f"{i+1}. {query}")
    print("0. Enter your own query")
    
    choice = input("\nEnter your choice (0-5): ")
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            query = input("\nEnter your query: ")
        elif 1 <= choice_num <= len(queries):
            query = queries[choice_num - 1]
        else:
            print("Invalid choice. Using the first query.")
            query = queries[0]
    except ValueError:
        print("Invalid input. Using the first query.")
        query = queries[0]
    
    print(f"\nSearching for: {query}")
    
    # Standard search
    print("\nPerforming standard search...")
    standard_results = search_regulatory_sources(query)
    print_results(standard_results, "Standard Search Results")
    
    # Agent-based search
    print("\nPerforming agent-based search...")
    agent_results = search_with_agents(query)
    print_results(agent_results, "Agent-Based Search Results")
    
    # Format citations
    print("\nFormatting citations...")
    citations = format_citations(agent_results)
    
    print("\n" + "=" * 80)
    print(f"Citations ({len(citations)} results)")
    print("=" * 80)
    
    for i, citation in enumerate(citations):
        print(f"\n[{i+1}] {citation['source_name']}")
        print(f"    Citation: {citation['citation_text']}")

if __name__ == "__main__":
    main() 