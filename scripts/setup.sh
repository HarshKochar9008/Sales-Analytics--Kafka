#!/bin/bash

# Sales Analytics Pipeline Setup Script
# This script automates the initial setup of the sales analytics pipeline

set -e

echo "🚀 Setting up Sales Analytics Pipeline..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version is installed"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p plugins
    print_success "Directories created"
}

# Start infrastructure
start_infrastructure() {
    print_status "Starting infrastructure with Docker Compose..."
    
    # Initialize Airflow (first time only)
    print_status "Initializing Airflow..."
    docker-compose --profile init up airflow-init -d
    
    # Wait for initialization
    sleep 10
    
    # Start all services
    print_status "Starting all services..."
    docker-compose up -d
    
    print_success "Infrastructure started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U postgres; do
        sleep 2
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Kafka
    print_status "Waiting for Kafka..."
    until docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 &> /dev/null; do
        sleep 2
    done
    print_success "Kafka is ready"
    
    # Wait for Airflow
    print_status "Waiting for Airflow..."
    until curl -s http://localhost:8080/health &> /dev/null; do
        sleep 5
    done
    print_success "Airflow is ready"
}

# Create Kafka topic
create_kafka_topic() {
    print_status "Creating Kafka topic..."
    docker-compose exec -T kafka kafka-topics --create \
        --topic sales_data \
        --bootstrap-server localhost:9092 \
        --partitions 1 \
        --replication-factor 1 \
        --if-not-exists
    print_success "Kafka topic 'sales_data' created"
}

# Display setup summary
display_summary() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Services running:"
    echo "  • Zookeeper: http://localhost:2181"
    echo "  • Kafka: http://localhost:9092"
    echo "  • PostgreSQL: localhost:5050"
    echo "  • Airflow: http://localhost:8080 (admin/admin)"
    echo ""
    echo "Next steps:"
    echo "  1. Configure Airflow connection:"
    echo "     - Go to http://localhost:8080"
    echo "     - Login: admin/admin"
    echo "     - Admin → Connections"
    echo "     - Add PostgreSQL connection:"
    echo "       * Connection Id: sales_postgres"
    echo "       * Host: postgres"
    echo "       * Database: sales"
    echo "       * Login: postgres"
    echo "       * Password: yourpassword"
    echo ""
    echo "  2. Start data producer:"
    echo "     python3 data_producer.py"
    echo ""
    echo "  3. Launch dashboard:"
    echo "     streamlit run dashboard.py"
    echo ""
    echo "  4. Monitor ETL in Airflow:"
    echo "     - Enable sales_etl_dag"
    echo "     - Monitor DAG runs"
    echo ""
}

# Main setup function
main() {
    echo "=================================="
    echo "Sales Analytics Pipeline Setup"
    echo "=================================="
    echo ""
    
    check_docker
    check_python
    install_dependencies
    create_directories
    start_infrastructure
    wait_for_services
    create_kafka_topic
    display_summary
}

# Run main function
main "$@" 