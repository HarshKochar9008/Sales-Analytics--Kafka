-- Sales Analytics Database Schema
-- PostgreSQL schema for sales data

-- Create sales_data table
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
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_data(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales_data(created_at);

-- Create a view for daily sales summary
CREATE OR REPLACE VIEW daily_sales_summary AS
SELECT 
    DATE(timestamp) as sale_date,
    COUNT(*) as total_orders,
    SUM(quantity) as total_quantity,
    SUM(total_price) as total_revenue,
    AVG(total_price) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product) as unique_products
FROM sales_data
GROUP BY DATE(timestamp)
ORDER BY sale_date DESC;

-- Create a view for regional performance
CREATE OR REPLACE VIEW regional_performance AS
SELECT 
    region,
    COUNT(*) as total_orders,
    SUM(total_price) as total_revenue,
    AVG(total_price) as avg_order_value,
    SUM(quantity) as total_quantity
FROM sales_data
GROUP BY region
ORDER BY total_revenue DESC;

-- Create a view for product performance
CREATE OR REPLACE VIEW product_performance AS
SELECT 
    product,
    COUNT(*) as total_orders,
    SUM(quantity) as total_quantity,
    SUM(total_price) as total_revenue,
    AVG(price) as avg_price,
    AVG(total_price) as avg_order_value
FROM sales_data
GROUP BY product
ORDER BY total_revenue DESC;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sales_data TO your_user;
-- GRANT SELECT ON daily_sales_summary TO your_user;
-- GRANT SELECT ON regional_performance TO your_user;
-- GRANT SELECT ON product_performance TO your_user; 