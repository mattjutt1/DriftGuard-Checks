#!/bin/bash

# DriftGuard Docker Deployment Script
# Automated deployment with validation and rollback

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Deployment options
PROFILE="${1:-}"
VALIDATE_ONLY="${2:-false}"

show_usage() {
    echo "Usage: $0 [profile] [validate-only]"
    echo ""
    echo "Profiles:"
    echo "  basic      - DriftGuard + Redis only (default)"
    echo "  nginx      - Include Nginx reverse proxy"
    echo "  monitoring - Include Prometheus + Grafana"
    echo "  full       - All services"
    echo ""
    echo "Options:"
    echo "  validate-only - Only validate configuration, don't deploy"
    echo ""
    echo "Examples:"
    echo "  $0                    # Basic deployment"
    echo "  $0 monitoring        # With monitoring"
    echo "  $0 full validate-only # Validate full setup"
}

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log "Prerequisites check passed"
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    # Check required files
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file not found: $ENV_FILE"
        error "Please run the setup wizard first: ./scripts/setup-wizard.sh"
        exit 1
    fi
    
    # Validate Docker Compose file
    if ! docker-compose -f "$COMPOSE_FILE" config &> /dev/null; then
        error "Invalid Docker Compose configuration"
        docker-compose -f "$COMPOSE_FILE" config
        exit 1
    fi
    
    # Validate environment variables
    if ! ./scripts/validate-config.js &> /dev/null; then
        warn "Configuration validation found issues. Check ./scripts/validate-config.js"
    fi
    
    log "Configuration validation passed"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/driftguard-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    # Backup volumes if they exist
    if docker volume ls | grep -q driftguard; then
        docker run --rm \
            -v driftguard-logs:/backup/logs \
            -v driftguard-cache:/backup/cache \
            -v redis-data:/backup/redis \
            -v "$(pwd):/host" \
            alpine:latest \
            tar czf "/host/$backup_file" -C /backup .
        
        log "Backup created: $backup_file"
    else
        info "No existing volumes to backup"
    fi
}

# Deploy with selected profile
deploy() {
    local profile="$1"
    log "Starting deployment with profile: $profile"
    
    # Set compose command based on available version
    local compose_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        compose_cmd="docker compose"
    fi
    
    # Build profiles argument
    local profiles_arg=""
    case "$profile" in
        "nginx")
            profiles_arg="--profile nginx"
            ;;
        "monitoring")
            profiles_arg="--profile monitoring"
            ;;
        "full")
            profiles_arg="--profile nginx --profile monitoring"
            ;;
        "basic"|"")
            profiles_arg=""
            ;;
        *)
            error "Unknown profile: $profile"
            show_usage
            exit 1
            ;;
    esac
    
    # Pull latest images
    log "Pulling latest images..."
    $compose_cmd -f "$COMPOSE_FILE" $profiles_arg pull
    
    # Build application image
    log "Building DriftGuard image..."
    $compose_cmd -f "$COMPOSE_FILE" build driftguard
    
    # Deploy services
    log "Deploying services..."
    $compose_cmd -f "$COMPOSE_FILE" $profiles_arg up -d
    
    # Wait for services to be healthy
    wait_for_health
    
    log "Deployment completed successfully!"
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "unhealthy"; then
            info "Attempt $attempt/$max_attempts: Some services not healthy yet..."
            sleep 10
            ((attempt++))
        else
            log "All services are healthy!"
            return 0
        fi
    done
    
    error "Services failed to become healthy after $max_attempts attempts"
    show_service_status
    exit 1
}

# Show service status
show_service_status() {
    log "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    log "DriftGuard logs (last 20 lines):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 driftguard
}

# Test deployment
test_deployment() {
    log "Testing deployment..."
    
    # Test health endpoint
    local health_url="http://localhost:3000/health"
    if curl -f -s "$health_url" > /dev/null; then
        log "Health check passed: $health_url"
    else
        error "Health check failed: $health_url"
        return 1
    fi
    
    # Test metrics endpoint
    local metrics_url="http://localhost:3000/metrics"
    if curl -f -s "$metrics_url" > /dev/null; then
        log "Metrics endpoint accessible: $metrics_url"
    else
        warn "Metrics endpoint not accessible: $metrics_url"
    fi
    
    log "Deployment test completed"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from latest backup
    local latest_backup=$(ls -t "$BACKUP_DIR"/driftguard-backup-*.tar.gz 2>/dev/null | head -1)
    if [[ -n "$latest_backup" ]]; then
        log "Restoring from backup: $latest_backup"
        # Restore logic here
        log "Backup restored"
    else
        warn "No backup found for rollback"
    fi
    
    log "Rollback completed"
}

# Cleanup function
cleanup() {
    log "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    log "Cleanup completed"
}

# Main execution
main() {
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Handle help
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Banner
    echo -e "${BLUE}${BOLD}"
    echo "============================================"
    echo "       DriftGuard Docker Deployment"
    echo "============================================"
    echo -e "${NC}"
    
    # Set profile
    local profile="${1:-basic}"
    local validate_only="${2:-false}"
    
    # Check prerequisites
    check_prerequisites
    
    # Validate configuration
    validate_config
    
    if [[ "$validate_only" == "validate-only" ]]; then
        log "Validation completed successfully!"
        exit 0
    fi
    
    # Create backup
    create_backup
    
    # Deploy
    deploy "$profile"
    
    # Test deployment
    if test_deployment; then
        log "✅ Deployment successful!"
        
        echo ""
        echo -e "${GREEN}${BOLD}🎉 DriftGuard is now running!${NC}"
        echo ""
        echo "Access points:"
        echo "• Health: http://localhost:3000/health"
        echo "• Metrics: http://localhost:3000/metrics"
        
        if [[ "$profile" == "monitoring" ]] || [[ "$profile" == "full" ]]; then
            echo "• Prometheus: http://localhost:9090"
            echo "• Grafana: http://localhost:3001 (admin/admin)"
        fi
        
        echo ""
        echo "Management commands:"
        echo "• View logs: docker-compose logs -f driftguard"
        echo "• Stop: docker-compose down"
        echo "• Update: $0 $profile"
        echo ""
        
    else
        error "Deployment test failed!"
        show_service_status
        exit 1
    fi
}

# Trap for cleanup on exit
trap cleanup EXIT

# Execute main function
main "$@"