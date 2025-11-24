#!/bin/bash
# ============================================================================
# Deployment Script for Script Analysis System
# ============================================================================
# This script handles building, deploying, and managing the Docker container
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="screenplay-analysis"
CONTAINER_NAME="screenplay-web"
PORT=8014

# Get version from src/version.py
get_version() {
    if [ -f "src/version.py" ]; then
        grep "^__version__" src/version.py | head -1 | cut -d'"' -f2
    else
        echo "2.6.0"
    fi
}

# Get git commit hash
get_git_commit() {
    git rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

APP_VERSION=$(get_version)
GIT_COMMIT=$(get_git_commit)
IMAGE_TAG="${APP_VERSION}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_warning "docker-compose not found. Will use docker commands instead."
    fi

    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env file and add your API keys before deployment."
        read -p "Press Enter when ready to continue..."
    fi

    log_success "Prerequisites check completed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG} (commit: ${GIT_COMMIT})..."
    docker build \
        --build-arg APP_VERSION=${APP_VERSION} \
        --build-arg GIT_COMMIT=${GIT_COMMIT} \
        -t ${IMAGE_NAME}:${IMAGE_TAG} \
        -t ${IMAGE_NAME}:latest \
        .
    log_success "Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
}

# Stop and remove existing container
stop_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Stopping existing container..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        log_success "Existing container stopped and removed"
    fi
}

# Start container using docker-compose
start_with_compose() {
    log_info "Starting container with docker-compose..."
    docker-compose up -d
    log_success "Container started with docker-compose"
}

# Start container using docker run
start_with_docker() {
    log_info "Starting container with docker run..."

    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:8000 \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v screenplay-data:/data \
        -v "$(pwd)/examples:/app/examples:ro" \
        --restart unless-stopped \
        ${IMAGE_NAME}:${IMAGE_TAG}

    log_success "Container started successfully"
}

# View logs
view_logs() {
    log_info "Showing container logs (Ctrl+C to exit)..."
    docker logs -f ${CONTAINER_NAME}
}

# Check container status
check_status() {
    log_info "Checking container status..."

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_success "Container is running"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

        # Check health
        log_info "Checking health endpoint..."
        sleep 2
        if curl -f http://localhost:${PORT}/health &> /dev/null; then
            log_success "Health check passed"
            curl -s http://localhost:${PORT}/health | python3 -m json.tool || true
        else
            log_warning "Health check failed. Container may still be starting..."
        fi
    else
        log_error "Container is not running"
        exit 1
    fi
}

# Main deployment function
deploy() {
    echo "============================================"
    echo "  Script Analysis System - Deployment"
    echo "  Version: ${APP_VERSION} (${GIT_COMMIT})"
    echo "============================================"
    echo ""

    check_prerequisites
    echo ""

    build_image
    echo ""

    stop_container
    echo ""

    # Start container
    if command -v docker-compose &> /dev/null; then
        start_with_compose
    else
        start_with_docker
    fi
    echo ""

    check_status
    echo ""

    log_success "Deployment completed successfully!"
    echo ""
    echo "============================================"
    echo "  Access the application at:"
    echo "  http://localhost:${PORT}"
    echo "============================================"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker logs -f ${CONTAINER_NAME}"
    echo "  Stop:         docker stop ${CONTAINER_NAME}"
    echo "  Restart:      docker restart ${CONTAINER_NAME}"
    echo "  Remove:       docker rm -f ${CONTAINER_NAME}"
    echo ""
}

# Command handling
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    build)
        build_image
        ;;
    start)
        if command -v docker-compose &> /dev/null; then
            start_with_compose
        else
            start_with_docker
        fi
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        if command -v docker-compose &> /dev/null; then
            start_with_compose
        else
            start_with_docker
        fi
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    version)
        echo "============================================"
        echo "  Version Information"
        echo "============================================"
        echo "  App Version:  ${APP_VERSION}"
        echo "  Git Commit:   ${GIT_COMMIT}"
        echo "  Git Branch:   $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
        echo "  Image Tag:    ${IMAGE_NAME}:${IMAGE_TAG}"
        echo "============================================"
        ;;
    *)
        echo "Usage: $0 {deploy|build|start|stop|restart|logs|status|version}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (build + start)"
        echo "  build    - Build Docker image only"
        echo "  start    - Start container"
        echo "  stop     - Stop container"
        echo "  restart  - Restart container"
        echo "  logs     - View container logs"
        echo "  status   - Check container status"
        echo "  version  - Show version information"
        exit 1
        ;;
esac
