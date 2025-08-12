#!/bin/bash

# Start script for DriftGuard with Redis
# Intelligently detects and uses existing Redis or starts a new one

set -e

echo "🚀 Starting DriftGuard Checks App with Redis..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is already running
check_redis() {
    if redis-cli ping &>/dev/null; then
        echo -e "${GREEN}✅ Redis is already running locally${NC}"
        return 0
    elif docker ps | grep -q redis; then
        echo -e "${GREEN}✅ Redis is running in Docker${NC}"
        # Get the Redis container port
        REDIS_PORT=$(docker ps | grep redis | grep -oP '0.0.0.0:\K[0-9]+' | head -1)
        if [ -z "$REDIS_PORT" ]; then
            REDIS_PORT=6379
        fi
        echo -e "${GREEN}   Using port: $REDIS_PORT${NC}"
        return 0
    else
        return 1
    fi
}

# Start Redis if needed
start_redis() {
    echo -e "${YELLOW}⚠️  Redis not found, starting Redis container...${NC}"
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        echo "Starting Redis using docker-compose..."
        docker-compose up -d redis
        
        # Wait for Redis to be ready
        echo "Waiting for Redis to be ready..."
        for i in {1..30}; do
            if docker-compose exec -T redis redis-cli ping &>/dev/null; then
                echo -e "${GREEN}✅ Redis is ready!${NC}"
                return 0
            fi
            echo -n "."
            sleep 1
        done
        
        echo -e "${RED}❌ Redis failed to start${NC}"
        return 1
    else
        # Fallback: start Redis directly with Docker
        echo "Starting Redis container directly..."
        docker run -d \
            --name driftguard-redis \
            -p 6379:6379 \
            -v driftguard-redis-data:/data \
            redis:7-alpine \
            redis-server --appendonly yes
        
        # Wait for Redis
        sleep 3
        
        if docker exec driftguard-redis redis-cli ping &>/dev/null; then
            echo -e "${GREEN}✅ Redis started successfully${NC}"
            return 0
        else
            echo -e "${RED}❌ Failed to start Redis${NC}"
            return 1
        fi
    fi
}

# Check environment file
check_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}Creating .env from .env.example...${NC}"
            cp .env.example .env
            echo -e "${YELLOW}⚠️  Please update .env with your actual values${NC}"
            echo "Press Enter to continue or Ctrl+C to exit and configure..."
            read
        else
            echo -e "${RED}❌ No .env file found${NC}"
            echo "Please create a .env file with required configuration"
            exit 1
        fi
    fi
}

# Build the application
build_app() {
    echo -e "${YELLOW}Building application...${NC}"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    # Build TypeScript
    echo "Building TypeScript..."
    npm run build
    
    echo -e "${GREEN}✅ Build complete${NC}"
}

# Main execution
main() {
    echo "═══════════════════════════════════════════════"
    echo "   DriftGuard Checks App - Startup Script"
    echo "═══════════════════════════════════════════════"
    echo ""
    
    # Check for Redis
    if ! check_redis; then
        start_redis || {
            echo -e "${RED}Failed to start Redis. Exiting.${NC}"
            exit 1
        }
    fi
    
    # Check environment
    check_env
    
    # Build application
    build_app
    
    # Set environment variables
    export NODE_ENV=${NODE_ENV:-development}
    export REDIS_URL=${REDIS_URL:-redis://localhost:6379}
    export ENABLE_ASYNC=true
    export ENABLE_WEBHOOK_VALIDATION=true
    export ENABLE_RATE_LIMITING=true
    export ENABLE_REPLAY_PROTECTION=true
    
    # Show configuration
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "   Configuration"
    echo "═══════════════════════════════════════════════"
    echo "NODE_ENV: $NODE_ENV"
    echo "REDIS_URL: $REDIS_URL"
    echo "Security Features:"
    echo "  ✅ Webhook Validation"
    echo "  ✅ Rate Limiting"
    echo "  ✅ Replay Protection"
    echo "  ✅ Async Processing"
    echo ""
    
    # Start the application
    echo -e "${GREEN}🚀 Starting DriftGuard application...${NC}"
    echo "═══════════════════════════════════════════════"
    echo ""
    
    if [ "$NODE_ENV" = "development" ]; then
        # Development mode with auto-reload
        npm run start:dev
    else
        # Production mode
        node dist/index-integrated.js
    fi
}

# Handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    
    # Only stop Redis if we started it
    if [ "$REDIS_STARTED" = "true" ]; then
        echo "Stopping Redis container..."
        docker stop driftguard-redis &>/dev/null || true
        docker rm driftguard-redis &>/dev/null || true
    fi
    
    echo -e "${GREEN}Goodbye!${NC}"
}

trap cleanup EXIT

# Run main function
main