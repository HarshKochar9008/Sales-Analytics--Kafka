# Sales Analytics Pipeline Makefile
# Provides convenient commands for managing the pipeline

.PHONY: help setup start stop restart clean logs producer dashboard airflow status

# Default target
help:
	@echo "Sales Analytics Pipeline - Available Commands"
	@echo "============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Complete initial setup (Docker + Dependencies)"
	@echo "  install        - Install Python dependencies only"
	@echo ""
	@echo "Infrastructure Management:"
	@echo "  start          - Start all services (Kafka, PostgreSQL, Airflow)"
	@echo "  stop           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo "  status         - Show status of all services"
	@echo ""
	@echo "Data Pipeline:"
	@echo "  producer       - Start the data producer"
	@echo "  dashboard      - Launch the Streamlit dashboard"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs           - Show logs from all services"
	@echo "  logs-kafka     - Show Kafka logs"
	@echo "  logs-airflow   - Show Airflow logs"
	@echo "  logs-postgres  - Show PostgreSQL logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          - Remove all containers and volumes"
	@echo "  reset          - Clean and setup from scratch"
	@echo ""

# Setup and installation
setup:
	@echo "🚀 Setting up Sales Analytics Pipeline..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install:
	@echo "📦 Installing Python dependencies..."
	@pip install -r requirements.txt

# Infrastructure management
start:
	@echo "🔄 Starting infrastructure..."
	@docker-compose up -d
	@echo "✅ Infrastructure started"
	@echo "📊 Airflow: http://localhost:8080 (admin/admin)"
	@echo "🗄️  PostgreSQL: localhost:5432"
	@echo "📡 Kafka: localhost:9092"

stop:
	@echo "🛑 Stopping infrastructure..."
	@docker-compose down
	@echo "✅ Infrastructure stopped"

restart:
	@echo "🔄 Restarting infrastructure..."
	@docker-compose down
	@docker-compose up -d
	@echo "✅ Infrastructure restarted"

status:
	@echo "📊 Service Status:"
	@docker-compose ps

# Data pipeline
producer:
	@echo "🎯 Starting data producer..."
	@python scripts/start_producer.py

dashboard:
	@echo "📊 Launching dashboard..."
	@streamlit run dashboard.py

# Monitoring
logs:
	@echo "📋 Showing all logs..."
	@docker-compose logs -f

logs-kafka:
	@echo "📋 Showing Kafka logs..."
	@docker-compose logs -f kafka

logs-airflow:
	@echo "📋 Showing Airflow logs..."
	@docker-compose logs -f airflow-webserver airflow-scheduler

logs-postgres:
	@echo "📋 Showing PostgreSQL logs..."
	@docker-compose logs -f postgres

# Maintenance
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleanup complete"

reset: clean setup
	@echo "🔄 Reset complete"

# Development helpers
init-airflow:
	@echo "🔧 Initializing Airflow..."
	@docker-compose --profile init up airflow-init -d
	@echo "✅ Airflow initialized"

create-topic:
	@echo "📡 Creating Kafka topic..."
	@docker-compose exec kafka kafka-topics --create \
		--topic sales_data \
		--bootstrap-server localhost:9092 \
		--partitions 1 \
		--replication-factor 1 \
		--if-not-exists
	@echo "✅ Topic created"

test-connection:
	@echo "🔍 Testing connections..."
	@echo "Testing Kafka..."
	@docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 || echo "❌ Kafka not ready"
	@echo "Testing PostgreSQL..."
	@docker-compose exec postgres pg_isready -U postgres || echo "❌ PostgreSQL not ready"
	@echo "Testing Airflow..."
	@curl -s http://localhost:8080/health > /dev/null && echo "✅ Airflow ready" || echo "❌ Airflow not ready"

# Quick start (setup + start + producer)
quick-start: setup start
	@echo "🎉 Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Configure Airflow connection (see README)"
	@echo "2. Run 'make producer' to start generating data"
	@echo "3. Run 'make dashboard' to view analytics" 