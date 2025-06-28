"""
Sales ETL DAG
Consumes data from Kafka and loads into PostgreSQL
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import json
import pandas as pd
from kafka import KafkaConsumer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'sales_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'sales_data'

# PostgreSQL configuration
POSTGRES_CONN_ID = 'sales_postgres'

def create_kafka_consumer():
    """Create and return Kafka consumer"""
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sales_etl_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=10000  # 10 seconds timeout
        )
        logger.info(f"Connected to Kafka topic: {TOPIC_NAME}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        raise

def consume_and_load(**context):
    """Consume messages from Kafka and load into PostgreSQL"""
    execution_date = context['execution_date']
    logger.info(f"Starting ETL process for execution date: {execution_date}")
    
    try:
        # Create Kafka consumer
        consumer = create_kafka_consumer()
        
        # Collect messages
        messages = []
        message_count = 0
        
        for message in consumer:
            messages.append(message.value)
            message_count += 1
            
            # Limit batch size to prevent memory issues
            if message_count >= 100:
                break
        
        consumer.close()
        
        if not messages:
            logger.info("No messages found in Kafka topic")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(messages)
        
        # Data validation and cleaning
        df = df.dropna(subset=['order_id', 'product', 'quantity', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['total_price'] = df['quantity'] * df['price']
        
        logger.info(f"Processing {len(df)} sales records")
        
        # Load into PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        engine = pg_hook.get_sqlalchemy_engine()
        
        # Insert data
        df.to_sql(
            'sales_data',
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
        
        logger.info(f"Successfully loaded {len(df)} records to PostgreSQL")
        
        # Log summary statistics
        total_revenue = df['total_price'].sum()
        avg_order_value = df['total_price'].mean()
        top_product = df.groupby('product')['quantity'].sum().idxmax()
        
        logger.info(f"Summary - Total Revenue: ${total_revenue:,.2f}")
        logger.info(f"Summary - Avg Order Value: ${avg_order_value:,.2f}")
        logger.info(f"Summary - Top Product: {top_product}")
        
    except Exception as e:
        logger.error(f"Error in ETL process: {e}")
        raise

def create_sales_table():
    """Create sales_data table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sales_data (
        order_id VARCHAR(255) PRIMARY KEY,
        product VARCHAR(100) NOT NULL,
        quantity INTEGER NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        customer_id VARCHAR(255) NOT NULL,
        region VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON sales_data(timestamp);
    CREATE INDEX IF NOT EXISTS idx_sales_region ON sales_data(region);
    CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_data(product);
    """
    
    try:
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        pg_hook.run(create_table_sql)
        logger.info("Sales table created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise

# Define DAG
with DAG(
    'sales_etl_dag',
    default_args=default_args,
    description='Sales ETL pipeline from Kafka to PostgreSQL',
    schedule_interval='*/1 * * * *',  # Every minute
    catchup=False,
    tags=['sales', 'etl', 'kafka', 'postgresql']
) as dag:
    
    # Task to create table
    create_table_task = PythonOperator(
        task_id='create_sales_table',
        python_callable=create_sales_table,
        doc="Create sales_data table if it doesn't exist"
    )
    
    # Main ETL task
    etl_task = PythonOperator(
        task_id='consume_kafka_store_postgres',
        python_callable=consume_and_load,
        doc="Consume from Kafka and load to PostgreSQL"
    )
    
    # Set task dependencies
    create_table_task >> etl_task 