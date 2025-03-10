#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking service status...${NC}\n"

# Check backend status
echo -e "${YELLOW}Backend (Port 8000):${NC}"
if curl -s http://localhost:8000/ > /dev/null; then
  echo -e "${GREEN}✅ Backend is running${NC}"
  
  # Get more details
  RESPONSE=$(curl -s http://localhost:8000/)
  echo -e "   Response: $RESPONSE"
else
  echo -e "${RED}❌ Backend is not running${NC}"
fi

echo ""

# Check frontend status
echo -e "${YELLOW}Frontend (Port 3000):${NC}"
if curl -s http://localhost:3000/ > /dev/null; then
  echo -e "${GREEN}✅ Frontend is running${NC}"
else
  echo -e "${RED}❌ Frontend is not running${NC}"
fi

echo ""

# Check if Docker containers are running
if command -v docker &> /dev/null; then
  echo -e "${YELLOW}Docker Containers:${NC}"
  
  BACKEND_CONTAINER=$(docker ps --filter "name=docai_backend" --format "{{.Names}}")
  if [ ! -z "$BACKEND_CONTAINER" ]; then
    echo -e "${GREEN}✅ Backend container is running: $BACKEND_CONTAINER${NC}"
  else
    echo -e "${RED}❌ Backend container is not running${NC}"
  fi
  
  FRONTEND_CONTAINER=$(docker ps --filter "name=docai_frontend" --format "{{.Names}}")
  if [ ! -z "$FRONTEND_CONTAINER" ]; then
    echo -e "${GREEN}✅ Frontend container is running: $FRONTEND_CONTAINER${NC}"
  else
    echo -e "${RED}❌ Frontend container is not running${NC}"
  fi
else
  echo -e "${YELLOW}Docker is not installed or not in PATH. Skipping container checks.${NC}"
fi 