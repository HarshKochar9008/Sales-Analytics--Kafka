#!/usr/bin/env python3
"""
Database Test Script
Test database connection and check if tables exist
"""

import psycopg2
import pandas as pd

# Database configuration (same as dashboard)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sales',
    'user': 'postgres',
    'password': 'postdata',
    'port': '5050'
}

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_tables(conn):
    """Check if required tables exist"""
    try:
        cursor = conn.cursor()
        
        # Check if sales_data table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sales_data'
            );
        """)
        sales_data_exists = cursor.fetchone()[0]
        
        # Check if views exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.views 
                WHERE view_name = 'daily_sales_summary'
            );
        """)
        daily_summary_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.views 
                WHERE view_name = 'regional_performance'
            );
        """)
        regional_performance_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.views 
                WHERE view_name = 'product_performance'
            );
        """)
        product_performance_exists = cursor.fetchone()[0]
        
        print("\n📊 Table Status:")
        print(f"  sales_data: {'✅' if sales_data_exists else '❌'}")
        print(f"  daily_sales_summary: {'✅' if daily_summary_exists else '❌'}")
        print(f"  regional_performance: {'✅' if regional_performance_exists else '❌'}")
        print(f"  product_performance: {'✅' if product_performance_exists else '❌'}")
        
        # Check data count
        if sales_data_exists:
            cursor.execute("SELECT COUNT(*) FROM sales_data;")
            count = cursor.fetchone()[0]
            print(f"\n📈 Data Count: {count} records in sales_data")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

def main():
    print("🔍 Testing Database Setup...")
    print("=" * 40)
    
    conn = test_connection()
    if conn:
        check_tables(conn)
        conn.close()
        
        print("\n💡 Next Steps:")
        if conn:
            print("  1. If tables are missing, run: ./scripts/setup.sh")
            print("  2. Or start Docker services: docker-compose up -d")
            print("  3. Then run your dashboard: streamlit run dashboard.py")
        else:
            print("  1. Make sure PostgreSQL is running")
            print("  2. Check your database configuration")
            print("  3. Run: docker-compose up -d")

if __name__ == "__main__":
    main()