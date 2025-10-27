#!/bin/bash

# Production Deployment Script
# Automated deployment with health checks and rollback

set -e

# Configuration
APP_NAME="ai-assistant"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="backups"
LOG_FILE="deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        error ".env file not found"
        exit 1
    fi
    
    # Check required environment variables
    source .env
    if [ -z "$GROQ_API_KEY" ]; then
        error "GROQ_API_KEY not set in .env file"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p $BACKUP_DIR
    BACKUP_NAME="${APP_NAME}-backup-$(date +%Y%m%d-%H%M%S)"
    
    # Backup database
    if docker-compose ps db | grep -q "Up"; then
        docker-compose exec -T db pg_dump -U postgres ai_assistant > "$BACKUP_DIR/$BACKUP_NAME.sql"
        success "Database backup created: $BACKUP_DIR/$BACKUP_NAME.sql"
    fi
    
    # Backup volumes
    docker run --rm -v ai-assistant_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/$BACKUP_NAME-postgres.tar.gz -C /data .
    docker run --rm -v ai-assistant_redis_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/$BACKUP_NAME-redis.tar.gz -C /data .
    
    success "Volume backups created"
}

# Build and deploy
deploy() {
    log "Starting deployment..."
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose pull
    
    # Build application
    log "Building application..."
    docker-compose build --no-cache app
    
    # Run database migrations
    log "Running database migrations..."
    docker-compose run --rm app flask db upgrade
    
    # Start services
    log "Starting services..."
    docker-compose up -d
    
    success "Services started"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check application health
    for i in {1..30}; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            success "Application health check passed"
            return 0
        fi
        log "Health check attempt $i/30 failed, retrying in 10 seconds..."
        sleep 10
    done
    
    error "Application health check failed"
    return 1
}

# Rollback function
rollback() {
    error "Deployment failed, initiating rollback..."
    
    # Stop current services
    docker-compose down
    
    # Restore from backup if available
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/*.sql 2>/dev/null | head -n1)
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring database from backup: $LATEST_BACKUP"
        docker-compose up -d db
        sleep 10
        docker-compose exec -T db psql -U postgres -d ai_assistant < "$LATEST_BACKUP"
    fi
    
    # Start previous version
    docker-compose up -d
    
    warning "Rollback completed"
}

# Cleanup old backups
cleanup() {
    log "Cleaning up old backups..."
    
    # Keep only last 5 backups
    ls -t $BACKUP_DIR/*.sql 2>/dev/null | tail -n +6 | xargs -r rm
    ls -t $BACKUP_DIR/*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
    
    # Clean up unused Docker images
    docker image prune -f
    
    success "Cleanup completed"
}

# Main deployment process
main() {
    log "Starting deployment process for $APP_NAME"
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Deploy
    if deploy; then
        # Health check
        if health_check; then
            success "Deployment completed successfully!"
            
            # Cleanup
            cleanup
            
            # Show status
            log "Service status:"
            docker-compose ps
            
        else
            # Rollback on health check failure
            rollback
            exit 1
        fi
    else
        error "Deployment failed"
        rollback
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    "backup")
        create_backup
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|backup|cleanup}"
        exit 1
        ;;
esac