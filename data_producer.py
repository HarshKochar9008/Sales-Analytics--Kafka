#!/usr/bin/env python3
"""
Sales Data Producer
Generates fake sales data and publishes to Kafka topic
"""

from kafka import KafkaProducer
import json
import time
import random
from faker import Faker
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'sales_data'

# Product catalog
PRODUCTS = [
    'Laptop', 'Phone', 'Headphones', 'Camera', 'Tablet', 
    'Smartwatch', 'Speaker', 'Monitor', 'Keyboard', 'Mouse'
]

# Regions
REGIONS = ['North', 'South', 'East', 'West', 'Central']

def create_kafka_producer():
    """Create and return Kafka producer"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        return producer
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        raise

def generate_sales_data():
    """Generate a single sales record"""
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 5)
    price = round(random.uniform(100, 2000), 2)
    
    data = {
        "order_id": fake.uuid4(),
        "product": product,
        "quantity": quantity,
        "price": price,
        "customer_id": fake.uuid4(),
        "region": random.choice(REGIONS),
        "timestamp": datetime.now().isoformat(),
        "total_price": round(quantity * price, 2)
    }
    return data

def main():
    """Main function to produce sales data"""
    logger.info("Starting Sales Data Producer...")
    
    try:
        producer = create_kafka_producer()
        
        while True:
            # Generate sales data
            sales_data = generate_sales_data()
            
            # Send to Kafka
            future = producer.send(
                TOPIC_NAME, 
                value=sales_data,
                key=sales_data['order_id']
            )
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Sent sales data: Order {sales_data['order_id'][:8]}... "
                f"Product: {sales_data['product']}, "
                f"Quantity: {sales_data['quantity']}, "
                f"Total: ${sales_data['total_price']}"
            )
            
            # Random sleep between 5-10 seconds
            sleep_time = random.uniform(5, 10)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
        producer.close()
    except Exception as e:
        logger.error(f"Error in producer: {e}")
        producer.close()
        raise

if __name__ == "__main__":
    main() 