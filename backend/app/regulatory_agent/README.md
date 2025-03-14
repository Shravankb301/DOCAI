# Regulatory Search Agent

A containerized service for searching and analyzing regulatory information from various sources including SEC EDGAR, Federal Register, and other regulatory databases.

## Features

- Search SEC EDGAR database and website
- Search Federal Register
- Analyze regulatory documents for key points, requirements, and deadlines
- RESTful API for easy integration
- Containerized deployment with health monitoring

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. Set up your environment:
   ```bash
   # Create a .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

2. Build and start the service:
   ```bash
   docker-compose up --build
   ```

3. The service will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

### Search
```
POST /search
Content-Type: application/json

{
    "query": "What are the latest SEC regulations regarding cryptocurrency?"
}
```
Searches for regulatory information based on the provided query.

### Root
```
GET /
```
Returns API information and available endpoints.

## Response Format

The search endpoint returns results in the following format:
```json
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
    "summary": "A concise summary of the findings",
    "error": false
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Successful request
- 500: Internal server error with error details

## Development

To modify the agent's behavior, update the following files:
- `main.py`: FastAPI server and endpoints
- `models/regulatory_agents_new.py`: Core agent logic
- `utils/openai_manager.py`: OpenAI integration

## Deployment

1. Build the Docker image:
   ```bash
   docker build -t regulatory-agent .
   ```

2. Run with Docker:
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here regulatory-agent
   ```

Or use Docker Compose:
```bash
docker-compose up
```

## Testing

Test the API using curl:
```bash
# Health check
curl http://localhost:8000/health

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest SEC regulations regarding cryptocurrency?"}'
```

## License

MIT License 