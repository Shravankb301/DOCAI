# DocAI Regulatory Compliance Backend

This is the backend for the DocAI Regulatory Compliance application, which provides tools for analyzing documents for regulatory compliance.

## New Feature: Regulatory Data Search Agents

We've enhanced the regulatory data search capabilities by implementing agent-based search functionality. This allows the system to search for regulatory data from various sources, including:

1. Built-in regulatory sources
2. Web search results
3. Regulatory APIs

### How It Works

The agent-based search system uses LangChain to create intelligent agents that can:

- Search for regulatory data using the existing database of sources
- Perform web searches for additional regulatory information
- Query regulatory APIs for up-to-date information
- Extract and structure the results into a consistent format

### Dependencies

The agent-based search functionality requires the following dependencies:

```
langchain>=0.0.200
openai>=0.27.0
duckduckgo-search>=3.8.0
google-api-python-client>=2.86.0
beautifulsoup4>=4.12.0
lxml>=4.9.2
```

These dependencies are included in the `requirements.txt` file.

### Implementation Details

The implementation consists of the following components:

1. `regulatory_agents.py`: Contains the `RegulatorySearchAgent` class and the `search_with_agents` function
2. Updates to `compliance.py`: Modified to use the agent-based search when available
3. Updates to `public_data.py`: Enhanced with more regulatory sources and improved search functionality

### Fallback Mechanism

The system is designed to gracefully fall back to the standard search functionality if:

- The required dependencies are not installed
- The agent-based search encounters an error
- The agent-based search returns no results

### Example Usage

An example script is provided in `examples/regulatory_search_example.py` to demonstrate how to use the regulatory agents. You can run it with:

```
python -m examples.regulatory_search_example
```

The script allows you to:
- Select from predefined queries or enter your own
- Compare results from standard search and agent-based search
- See formatted citations for the search results

### Testing

A test script is provided in `tests/test_regulatory_agents.py` to verify the functionality of the regulatory agents.

## Installation

1. Clone the repository
2. Install the dependencies: `pip install -r requirements.txt`
3. Run the application: `uvicorn app.main:app --reload`

## Testing

Run the tests using pytest:

```
pytest tests/
```

Or run a specific test:

```
python -m tests.test_regulatory_agents
``` 