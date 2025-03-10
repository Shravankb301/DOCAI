#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
  local port=$1
  local service=$2
  echo -e "${YELLOW}Checking if port $port is already in use...${NC}"
  
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
    local pid=$(lsof -ti:$port)
    echo -e "${RED}Port $port is in use by process $pid. Killing process...${NC}"
    kill -9 $pid
    sleep 2
    echo -e "${GREEN}Port $port is now available for $service.${NC}"
  else
    echo -e "${GREEN}Port $port is available for $service.${NC}"
  fi
}

# Function to handle exit
cleanup() {
  echo -e "\n${YELLOW}Stopping services...${NC}"
  if [ ! -z "$BACKEND_PID" ]; then
    echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
  fi
  
  if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
  fi
  
  echo -e "${GREEN}All services stopped.${NC}"
  exit 0
}

# Trap SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Check if required ports are available
check_port 8000 "Backend"
check_port 3000 "Frontend"

# Start the backend
echo -e "\n${YELLOW}Starting backend...${NC}"
cd backend
python3 run.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while ! curl -s http://localhost:8000/ > /dev/null; do
  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Backend failed to start after $MAX_RETRIES attempts.${NC}"
    cleanup
    exit 1
  fi
  
  echo -e "${YELLOW}Waiting for backend to become available... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)${NC}"
  sleep 2
  RETRY_COUNT=$((RETRY_COUNT+1))
done

echo -e "${GREEN}Backend started successfully!${NC}"

# Start the frontend
echo -e "\n${YELLOW}Starting frontend...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
RETRY_COUNT=0

while ! curl -s http://localhost:3000/ > /dev/null; do
  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Frontend failed to start after $MAX_RETRIES attempts.${NC}"
    cleanup
    exit 1
  fi
  
  echo -e "${YELLOW}Waiting for frontend to become available... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)${NC}"
  sleep 2
  RETRY_COUNT=$((RETRY_COUNT+1))
done

echo -e "${GREEN}Frontend started successfully!${NC}"

# Display success message
echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}🚀 All services are running!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}Backend: http://localhost:8000${NC}"
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services.${NC}"

# Keep script running
wait 