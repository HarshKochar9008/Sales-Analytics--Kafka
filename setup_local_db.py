#!/usr/bin/env python3
"""
Local Database Setup Script
Set up PostgreSQL database with schema and sample data
"""

import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import random

# Database configuration (your local setup)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sales',
    'user': 'postgres',
    'password': 'postdata',
    'port': '5050'
}

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if sales database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='sales'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE sales")
            print("✅ Created 'sales' database")
        else:
            print("✅ 'sales' database already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def create_schema():
    """Create tables and views"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read schema from file
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Database schema created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False
    
    return True

def generate_sample_data():
    """Generate sample sales data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Sample data
        products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 'Monitor', 'Speaker']
        regions = ['North', 'South', 'East', 'West', 'Central']
        
        # Generate 100 sample records
        for i in range(100):
            order_id = f"ORD-{i+1:04d}"
            product = random.choice(products)
            quantity = random.randint(1, 5)
            price = round(random.uniform(50, 1000), 2)
            customer_id = f"CUST-{random.randint(1000, 9999)}"
            region = random.choice(regions)
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
            total_price = price * quantity
            
            cursor.execute("""
                INSERT INTO sales_data (order_id, product, quantity, price, customer_id, region, timestamp, total_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
            """, (order_id, product, quantity, price, customer_id, region, timestamp, total_price))
        
        conn.commit()
        print("✅ Generated 100 sample sales records")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        return False
    
    return True

def main():
    print("🔧 Setting up Local PostgreSQL Database...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database")
        return
    
    # Step 2: Create schema
    if not create_schema():
        print("❌ Failed to create schema")
        return
    
    # Step 3: Generate sample data
    if not generate_sample_data():
        print("❌ Failed to generate sample data")
        return
    
    print("\n🎉 Database setup complete!")
    print("You can now run: streamlit run dashboard.py")

if __name__ == "__main__":
    main() 