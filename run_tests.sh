#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
  echo -e "${BLUE}DocAI Testing Script${NC}"
  echo -e "Usage: ./run_tests.sh [options]"
  echo -e ""
  echo -e "Options:"
  echo -e "  -h, --help       Show this help message"
  echo -e "  -b, --backend    Run only backend tests"
  echo -e "  -f, --frontend   Run only frontend tests"
  echo -e "  -e, --e2e        Run only end-to-end tests"
  echo -e "  -a, --all        Run all tests (default)"
  echo -e "  -c, --coverage   Generate coverage reports"
  echo -e ""
}

# Default options
RUN_BACKEND=false
RUN_FRONTEND=false
RUN_E2E=false
GENERATE_COVERAGE=false

# Parse command line arguments
if [ $# -eq 0 ]; then
  # If no arguments, run only backend and frontend tests (skip E2E)
  RUN_BACKEND=true
  RUN_FRONTEND=true
  RUN_E2E=false
else
  while [ "$1" != "" ]; do
    case $1 in
      -h | --help )
        show_help
        exit 0
        ;;
      -b | --backend )
        RUN_BACKEND=true
        ;;
      -f | --frontend )
        RUN_FRONTEND=true
        ;;
      -e | --e2e )
        RUN_E2E=true
        ;;
      -a | --all )
        RUN_BACKEND=true
        RUN_FRONTEND=true
        RUN_E2E=true
        ;;
      -c | --coverage )
        GENERATE_COVERAGE=true
        ;;
      * )
        echo -e "${RED}Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
    esac
    shift
  done
fi

# Function to run backend tests
run_backend_tests() {
  echo -e "\n${YELLOW}Running backend tests...${NC}"
  cd backend
  
  if [ "$GENERATE_COVERAGE" = true ]; then
    echo -e "${BLUE}Running backend tests with coverage...${NC}"
    python3 -m pytest tests/unit tests/integration --cov=app --cov-report=term --cov-report=html
  else
    echo -e "${BLUE}Running backend unit tests...${NC}"
    python3 -m pytest tests/unit
    
    echo -e "\n${BLUE}Running backend integration tests...${NC}"
    python3 -m pytest tests/integration
  fi
  
  TEST_EXIT_CODE=$?
  cd ..
  
  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Backend tests passed!${NC}"
  else
    echo -e "${RED}❌ Backend tests failed!${NC}"
    FAILED=true
  fi
}

# Function to run frontend tests
run_frontend_tests() {
  echo -e "\n${YELLOW}Running frontend tests...${NC}"
  cd frontend
  
  if [ "$GENERATE_COVERAGE" = true ]; then
    echo -e "${BLUE}Running frontend tests with coverage...${NC}"
    npm test -- --coverage
  else
    echo -e "${BLUE}Running frontend tests...${NC}"
    npm test
  fi
  
  TEST_EXIT_CODE=$?
  cd ..
  
  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend tests passed!${NC}"
  else
    echo -e "${RED}❌ Frontend tests failed!${NC}"
    FAILED=true
  fi
}

# Function to run E2E tests
run_e2e_tests() {
  echo -e "\n${YELLOW}Running E2E tests...${NC}"
  
  # Start backend and frontend servers
  echo -e "${BLUE}Starting backend server...${NC}"
  cd backend
  python3 run.py &
  BACKEND_PID=$!
  cd ..
  
  # Wait for backend to start
  echo -e "${BLUE}Waiting for backend to start...${NC}"
  sleep 10
  
  echo -e "${BLUE}Starting frontend development server...${NC}"
  cd frontend
  
  # Install Playwright if not already installed
  if ! command -v npx playwright &> /dev/null; then
    echo -e "${BLUE}Installing Playwright...${NC}"
    npx playwright install
  fi
  
  # Start the frontend development server
  npm run dev &
  FRONTEND_PID=$!
  
  # Wait for frontend to start
  echo -e "${BLUE}Waiting for frontend to start...${NC}"
  sleep 15
  
  # Run E2E tests
  echo -e "${BLUE}Running Playwright tests...${NC}"
  PLAYWRIGHT_TEST_BASE_URL=http://localhost:3000 npx playwright test
  
  TEST_EXIT_CODE=$?
  
  # Stop servers
  echo -e "${BLUE}Stopping servers...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  
  cd ..
  
  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ E2E tests passed!${NC}"
  else
    echo -e "${RED}❌ E2E tests failed!${NC}"
    FAILED=true
  fi
}

# Main execution
FAILED=false

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}🧪 Starting DocAI Test Suite${NC}"
echo -e "${BLUE}==================================================${NC}"

if [ "$RUN_BACKEND" = true ]; then
  run_backend_tests
fi

if [ "$RUN_FRONTEND" = true ]; then
  run_frontend_tests
fi

if [ "$RUN_E2E" = true ]; then
  run_e2e_tests
fi

echo -e "\n${BLUE}==================================================${NC}"
if [ "$FAILED" = true ]; then
  echo -e "${RED}❌ Some tests failed!${NC}"
  exit 1
else
  echo -e "${GREEN}✅ All tests passed!${NC}"
  exit 0
fi 