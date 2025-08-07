#!/bin/bash
# Infisical Management Script for PromptEvolver Development

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

COMPOSE_CMD="docker-compose --env-file .env.infisical -f docker-compose.infisical.yml"

case "$1" in
    start)
        echo -e "${BLUE}🚀 Starting Infisical services...${NC}"
        $COMPOSE_CMD up -d
        echo -e "${GREEN}✅ Infisical started at http://localhost:8080${NC}"
        ;;

    stop)
        echo -e "${YELLOW}🛑 Stopping Infisical services...${NC}"
        $COMPOSE_CMD down
        echo -e "${GREEN}✅ Infisical services stopped${NC}"
        ;;

    restart)
        echo -e "${YELLOW}🔄 Restarting Infisical services...${NC}"
        $COMPOSE_CMD down
        $COMPOSE_CMD up -d
        echo -e "${GREEN}✅ Infisical services restarted${NC}"
        ;;

    status)
        echo -e "${BLUE}📊 Infisical Service Status:${NC}"
        $COMPOSE_CMD ps
        ;;

    logs)
        if [ -n "$2" ]; then
            echo -e "${BLUE}📜 Showing logs for $2...${NC}"
            $COMPOSE_CMD logs -f "$2"
        else
            echo -e "${BLUE}📜 Showing all logs...${NC}"
            $COMPOSE_CMD logs -f
        fi
        ;;

    backup)
        echo -e "${BLUE}💾 Creating backup...${NC}"
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"

        # Backup database
        docker-compose --env-file .env.infisical -f docker-compose.infisical.yml exec -T infisical-db pg_dump -U infisical infisical > "$BACKUP_DIR/database.sql"

        # Backup configuration
        cp .env.infisical "$BACKUP_DIR/"
        cp docker-compose.infisical.yml "$BACKUP_DIR/"

        echo -e "${GREEN}✅ Backup created in $BACKUP_DIR${NC}"
        ;;

    reset)
        echo -e "${RED}⚠️  WARNING: This will delete ALL Infisical data!${NC}"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        if [ "$confirm" = "yes" ]; then
            echo -e "${YELLOW}🗑️  Resetting Infisical...${NC}"
            $COMPOSE_CMD down -v
            docker volume rm prompt-wizard_infisical_db_data prompt-wizard_infisical_redis_data 2>/dev/null || true
            rm -rf infisical-data/
            echo -e "${GREEN}✅ Infisical reset complete. Run setup-infisical.sh to reinstall${NC}"
        else
            echo -e "${BLUE}❌ Reset cancelled${NC}"
        fi
        ;;

    cli)
        echo -e "${BLUE}💻 Installing Infisical CLI...${NC}"
        if command -v npm &> /dev/null; then
            npm install -g @infisical/cli
            echo -e "${GREEN}✅ Infisical CLI installed${NC}"
            echo -e "${YELLOW}💡 Usage: infisical login --domain=http://localhost:8080${NC}"
        else
            echo -e "${RED}❌ npm not found. Please install Node.js first${NC}"
        fi
        ;;

    setup-project)
        echo -e "${BLUE}📋 Setting up PromptEvolver project in Infisical...${NC}"
        echo "This will guide you through creating the project structure:"
        echo ""
        echo "1. Go to http://localhost:8080"
        echo "2. Create a new project named 'PromptEvolver'"
        echo "3. Create environments: development, staging, production"
        echo "4. Add secrets for each feature:"
        echo ""
        echo -e "${YELLOW}Authentication Feature Secrets:${NC}"
        echo "  - JWT_SECRET_KEY"
        echo "  - JWT_REFRESH_SECRET"
        echo "  - OAUTH_CLIENT_ID"
        echo "  - OAUTH_CLIENT_SECRET"
        echo "  - SESSION_SECRET_KEY"
        echo ""
        echo -e "${YELLOW}Optimization Feature Secrets:${NC}"
        echo "  - OPENAI_API_KEY"
        echo "  - ANTHROPIC_API_KEY"
        echo "  - PROMPTWIZARD_CONFIG"
        echo "  - OLLAMA_BASE_URL"
        echo "  - AI_MODEL_CONFIG"
        echo ""
        echo -e "${YELLOW}Dashboard Feature Secrets:${NC}"
        echo "  - ANALYTICS_API_KEY"
        echo "  - MONITORING_TOKEN"
        echo "  - GRAFANA_API_KEY"
        echo "  - PROMETHEUS_CONFIG"
        echo "  - SENTRY_DSN"
        ;;

    *)
        echo -e "${BLUE}🔐 Infisical Management for PromptEvolver${NC}"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  start        Start Infisical services"
        echo "  stop         Stop Infisical services"
        echo "  restart      Restart Infisical services"
        echo "  status       Show service status"
        echo "  logs [service]  Show logs (optional: specific service)"
        echo "  backup       Create backup of data and config"
        echo "  reset        DANGER: Delete all data and reset"
        echo "  cli          Install Infisical CLI"
        echo "  setup-project  Guide for setting up PromptEvolver project"
        echo ""
        echo "Service names: infisical-backend, infisical-db, infisical-redis"
        ;;
esac
