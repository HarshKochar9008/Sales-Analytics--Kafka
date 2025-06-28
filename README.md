# 📊 Sales Analytics Pipeline

A real-time sales analytics pipeline built with Apache Kafka, Apache Airflow, PostgreSQL, and Streamlit. This project demonstrates a complete data engineering workflow from data ingestion to visualization.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Data Producer │───▶│    Kafka    │───▶│   Airflow    │───▶│ PostgreSQL  │
│   (Python)      │    │   (Stream)  │    │   (ETL)      │    │  (Storage)  │
└─────────────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │  Dashboard  │
                                                          │ (Streamlit) │
                                                          └─────────────┘
```

## 🚀 Tech Stack

| Component | Technology |
|-----------|------------|
| **Data Ingestion** | Apache Kafka |
| **Stream Producer** | Python (Mock script) |
| **Orchestration** | Apache Airflow |
| **Transformation** | Python, Pandas |
| **Storage** | PostgreSQL |
| **Visualization** | Streamlit, Plotly |

## 📁 Project Structure

```
sales-analytics/
├── data_producer.py          # Mock sales data generator
├── dashboard.py              # Streamlit dashboard
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Infrastructure setup
├── README.md                 # This file
├── airflow_dags/
│   └── sales_etl.py         # Airflow ETL DAG
└── database/
    └── schema.sql           # PostgreSQL schema
```

## 🛠️ Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd sales-analytics
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure with Docker

```bash
# Initialize Airflow (first time only)
docker-compose --profile init up airflow-init

# Start all services
docker-compose up -d
```

This will start:
- **Zookeeper** (port 2181)
- **Kafka** (port 9092)
- **PostgreSQL** (port 5432)
- **Airflow Webserver** (port 8080)
- **Airflow Scheduler**

### 4. Verify Services

```bash
# Check if all containers are running
docker-compose ps

# Check Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 5. Configure Airflow Connection

1. Open Airflow UI: http://localhost:8080
2. Login: `admin` / `admin`
3. Go to Admin → Connections
4. Add new connection:
   - **Connection Id**: `sales_postgres`
   - **Connection Type**: `Postgres`
   - **Host**: `postgres`
   - **Schema**: `sales`
   - **Login**: `postgres`
   - **Password**: `yourpassword`
   - **Port**: `5432`

## 🚀 Usage

### 1. Start Data Producer

```bash
python data_producer.py
```

This will generate mock sales data every 5-10 seconds and send it to Kafka.

### 2. Monitor Airflow DAG

1. Go to http://localhost:8080
2. Find the `sales_etl_dag`
3. Enable the DAG (toggle switch)
4. Monitor the ETL process

### 3. Launch Dashboard

```bash
streamlit run dashboard.py
```

Open http://localhost:8501 to view the real-time dashboard.

## 📊 Data Flow

### 1. Data Generation
- **Producer**: Generates fake sales data with fields:
  - `order_id`, `product`, `quantity`, `price`
  - `customer_id`, `region`, `timestamp`
- **Frequency**: Every 5-10 seconds
- **Destination**: Kafka topic `sales_data`

### 2. Data Processing
- **Airflow DAG**: Runs every minute
- **Process**: Consumes from Kafka, transforms with Pandas
- **Storage**: Loads into PostgreSQL with validation

### 3. Data Visualization
- **Dashboard**: Real-time metrics and charts
- **Features**: KPIs, regional analysis, product performance
- **Auto-refresh**: Every 30 seconds

## 📈 Dashboard Features

- **KPI Metrics**: Total revenue, orders, average order value, unique customers
- **Regional Analysis**: Revenue by region with interactive charts
- **Product Performance**: Top products by revenue
- **Sales Trends**: Daily revenue and order trends
- **Data Distribution**: Product quantity distribution
- **Recent Data**: Latest sales records

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sales
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=sales_data

# Airflow
AIRFLOW_UID=50000
```

### Customizing Data Generation

Edit `data_producer.py` to modify:
- Product catalog
- Price ranges
- Regions
- Generation frequency

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   ```bash
   # Check if Kafka is running
   docker-compose ps kafka
   
   # Check Kafka logs
   docker-compose logs kafka
   ```

2. **PostgreSQL Connection Failed**
   ```bash
   # Check PostgreSQL status
   docker-compose ps postgres
   
   # Check PostgreSQL logs
   docker-compose logs postgres
   ```

3. **Airflow DAG Not Running**
   - Verify connection in Airflow UI
   - Check DAG is enabled
   - Review scheduler logs: `docker-compose logs airflow-scheduler`

4. **Dashboard No Data**
   - Ensure data producer is running
   - Check ETL DAG is processing data
   - Verify database connection in dashboard

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs kafka
docker-compose logs airflow-webserver
docker-compose logs postgres
```

## 🔄 Development

### Adding New Data Sources

1. Create new producer script
2. Add new Kafka topic
3. Create new Airflow DAG
4. Update database schema
5. Extend dashboard

### Scaling

- **Kafka**: Add more brokers
- **Airflow**: Use CeleryExecutor for distributed processing
- **PostgreSQL**: Add read replicas
- **Dashboard**: Deploy with load balancer

## 📝 API Reference

### Kafka Topics

- `sales_data`: Raw sales data stream

### Database Tables

- `sales_data`: Main sales records
- `daily_sales_summary`: Daily aggregated data
- `regional_performance`: Regional metrics
- `product_performance`: Product metrics

### Airflow DAGs

- `sales_etl_dag`: Main ETL pipeline

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apache Kafka for stream processing
- Apache Airflow for workflow orchestration
- Streamlit for rapid dashboard development
- PostgreSQL for reliable data storage

---

**Happy Data Engineering! 🚀** 