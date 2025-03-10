#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all services...${NC}\n"

# Stop processes running on ports 8000 (backend) and 3000 (frontend)
BACKEND_PID=$(lsof -ti:8000)
if [ ! -z "$BACKEND_PID" ]; then
  echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
  kill -9 $BACKEND_PID 2>/dev/null
  echo -e "${GREEN}Backend stopped.${NC}"
else
  echo -e "${YELLOW}No backend process found running on port 8000.${NC}"
fi

FRONTEND_PID=$(lsof -ti:3000)
if [ ! -z "$FRONTEND_PID" ]; then
  echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
  kill -9 $FRONTEND_PID 2>/dev/null
  echo -e "${GREEN}Frontend stopped.${NC}"
else
  echo -e "${YELLOW}No frontend process found running on port 3000.${NC}"
fi

# Check if Docker is installed and stop containers if running
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
  if [ -f "docker-compose.yml" ]; then
    echo -e "\n${YELLOW}Stopping Docker containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Docker containers stopped.${NC}"
  else
    echo -e "\n${YELLOW}No docker-compose.yml file found in the current directory.${NC}"
  fi
fi

echo -e "\n${GREEN}All services have been stopped.${NC}" 