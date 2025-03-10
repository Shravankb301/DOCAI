# AI-Enabled Compliance System

An AI-powered system for checking document compliance using transformer models.

## Features

- Upload regulatory documents for compliance analysis
- AI-powered compliance checking using zero-shot classification
- Document categorization as "compliant" or "non-compliant"
- Confidence scores for compliance determinations
- Persistent storage of analysis results

## Architecture

- **Backend**: FastAPI with transformer models
- **Frontend**: Next.js with Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Containerization**: Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- Node.js (v14+) for local frontend development
- Python 3.8+ for local backend development
- Supabase account (optional, can use local storage)

## Setup Instructions

### Environment Variables

1. Backend:
   - Copy `backend/.env.example` to `backend/.env`
   - Update with your Supabase credentials (if using Supabase)

2. Frontend:
   - Create `frontend/.env.local` with the following:
     ```
     NEXT_PUBLIC_API_URL=http://localhost:8000
     NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
     NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

### Running with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Running Locally

#### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload a document or enter text content
3. Submit for compliance analysis
4. View the analysis results with compliance status and confidence score

## API Endpoints

- `POST /api/upload`: Upload a document for analysis
- `GET /api/status/{document_id}`: Check analysis status

## Database Schema

The `risks` table contains:
- `id`: Unique identifier
- `file_path`: Path to the uploaded document
- `status`: Compliance status
- `details`: Additional analysis information
- `created_at`: Timestamp of the analysis

## Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Orchestration

There are two ways to orchestrate the backend and frontend services:

### Using the run.sh Script

The `run.sh` script provides a convenient way to start both the backend and frontend services with a single command:

```bash
# Make the script executable
chmod +x run.sh

# Run the script
./run.sh
```

This script:
- Checks if the required ports (8000 for backend, 3000 for frontend) are available
- Starts the backend service and waits for it to be ready
- Starts the frontend service and waits for it to be ready
- Provides a clean way to stop both services with Ctrl+C

### Using Docker Compose

For a containerized approach, you can use Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

The Docker Compose configuration:
- Builds and runs both services in containers
- Sets up proper networking between the services
- Configures health checks to ensure services are running correctly
- Mounts volumes for persistent data and code changes

### Checking Service Status

You can check the status of the backend and frontend services using the `status.sh` script:

```bash
# Make the script executable
chmod +x status.sh

# Run the script
./status.sh
```

This script will:
- Check if the backend is running on port 8000
- Check if the frontend is running on port 3000
- Check if Docker containers are running (if Docker is installed)
- Display the status of each service with color-coded output

### Stopping Services

To stop all running services, you can use the `stop.sh` script:

```bash
# Make the script executable
chmod +x stop.sh

# Run the script
./stop.sh
```

This script will:
- Stop any process running on port 8000 (backend)
- Stop any process running on port 3000 (frontend)
- Stop Docker containers if Docker Compose is being used
- Display the status of each operation with color-coded output

## Development with Cursor

This project includes Cursor rules to help with development. These rules provide guidance and best practices for different aspects of the project.

### Available Rules

1. **FastAPI Best Practices**: Guidelines for backend development with FastAPI.
2. **Next.js Best Practices**: Guidelines for frontend development with Next.js.
3. **Orchestration Best Practices**: Guidelines for service orchestration, shell scripting, and containerization.
4. **Supabase Integration Best Practices**: Guidelines for integrating Supabase with both backend and frontend.
5. **AI Model Integration Best Practices**: Guidelines for integrating and using transformer models for document analysis.
6. **Continuous Testing Best Practices**: Guidelines for continuous testing, test-driven development, and ensuring implementations are working correctly.
7. **CI/CD and Automated Rebuilding Best Practices**: Guidelines for continuous integration, automated testing, and rebuilding failing implementations.

For more information about these rules, see the `.cursor/README.md` file.

## Continuous Testing and Automated Rebuilding

This project includes a comprehensive continuous testing and automated rebuilding system to ensure all implementations are working correctly.

### GitHub Actions Workflow

The project includes a GitHub Actions workflow for continuous testing and automated rebuilding:

```bash
.github/workflows/continuous-testing.yml
```

This workflow:
- Runs backend tests (unit and integration)
- Runs frontend tests
- Runs end-to-end tests
- Attempts to automatically fix common issues
- Generates a report of test results and rebuild actions

### Diagnostic and Fix Scripts

The project includes several scripts for diagnosing and fixing common issues:

- `scripts/ci/diagnose_test_failures.py`: Diagnoses backend test failures
- `scripts/ci/auto_fix_common_issues.py`: Automatically fixes common backend issues
- `scripts/ci/diagnose_frontend_failures.js`: Diagnoses frontend test failures

These scripts can be run manually to diagnose and fix issues:

```bash
# Diagnose backend test failures
python scripts/ci/diagnose_test_failures.py

# Automatically fix common backend issues
python scripts/ci/auto_fix_common_issues.py

# Diagnose frontend test failures
node scripts/ci/diagnose_frontend_failures.js
```

## License

MIT 