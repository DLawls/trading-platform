#!/bin/bash
# Alpaca Data Collector - Docker Runner Script

set -e

echo "🚀 Alpaca Data Collector - Docker Runner"
echo "========================================"

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the collector once"
    echo "  start     Start the collector service"
    echo "  stop      Stop the collector service"
    echo "  logs      Show collector logs"
    echo "  status    Show collector status"
    echo "  shell     Open shell in container"
    echo "  test      Test configuration"
    echo ""
}

# Function to build image
build_image() {
    echo "🔨 Building Alpaca collector Docker image..."
    docker build -t alpaca-data-collector .
    echo "✅ Image built successfully!"
}

# Function to run once
run_once() {
    echo "🏃 Running Alpaca collector once..."
    docker run --rm \
        -v "$(pwd)/../financial_data:/app/financial_data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config:ro" \
        alpaca-data-collector
}

# Function to start service
start_service() {
    echo "🚀 Starting Alpaca collector service..."
    docker-compose up -d
    echo "✅ Service started! Use './run_docker.sh logs' to monitor"
}

# Function to stop service
stop_service() {
    echo "🛑 Stopping Alpaca collector service..."
    docker-compose down
    echo "✅ Service stopped!"
}

# Function to show logs
show_logs() {
    echo "📋 Alpaca collector logs:"
    docker-compose logs -f alpaca-collector
}

# Function to show status
show_status() {
    echo "📊 Alpaca collector status:"
    docker-compose ps
    echo ""
    echo "📈 Recent logs:"
    docker-compose logs --tail=10 alpaca-collector
}

# Function to open shell
open_shell() {
    echo "🐚 Opening shell in Alpaca collector container..."
    docker run --rm -it \
        -v "$(pwd)/../financial_data:/app/financial_data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        alpaca-data-collector bash
}

# Function to test configuration
test_config() {
    echo "🧪 Testing Alpaca collector configuration..."
    docker run --rm \
        -v "$(pwd)/config:/app/config:ro" \
        alpaca-data-collector python3 test_config_only.py
}

# Main script logic
case "${1:-}" in
    build)
        build_image
        ;;
    run)
        build_image
        run_once
        ;;
    start)
        build_image
        start_service
        ;;
    stop)
        stop_service
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    shell)
        build_image
        open_shell
        ;;
    test)
        build_image
        test_config
        ;;
    "")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 