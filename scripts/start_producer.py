#!/usr/bin/env python3
"""
Start Data Producer Script
Simple script to start the sales data producer with monitoring
"""

import subprocess
import sys
import time
import signal
import os
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 Sales Data Producer")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Stopping data producer...")
    print("Thank you for using Sales Analytics Pipeline!")
    sys.exit(0)

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import kafka
        import faker
        import pandas
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_kafka_connection():
    """Check if Kafka is accessible"""
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: str(v).encode('utf-8')
        )
        producer.close()
        print("✅ Kafka connection successful")
        return True
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        print("Please ensure Kafka is running: docker-compose up -d")
        return False

def start_producer():
    """Start the data producer"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check Kafka connection
    if not check_kafka_connection():
        return False
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎯 Starting data producer...")
    print("📊 Generating sales data every 5-10 seconds")
    print("📤 Sending to Kafka topic: sales_data")
    print("")
    
    try:
        # Start the producer
        process = subprocess.Popen([
            sys.executable, "data_producer.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Monitor the process
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            
            # Check if process is still running
            if process.poll() is not None:
                print("❌ Data producer stopped unexpectedly")
                return False
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping data producer...")
        process.terminate()
        process.wait()
        print("✅ Data producer stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting producer: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Sales Data Producer")
        print("")
        print("Usage:")
        print("  python scripts/start_producer.py")
        print("")
        print("Options:")
        print("  --help    Show this help message")
        print("")
        print("This script will:")
        print("  • Check dependencies")
        print("  • Verify Kafka connection")
        print("  • Start generating sales data")
        print("  • Monitor the producer process")
        return
    
    success = start_producer()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 