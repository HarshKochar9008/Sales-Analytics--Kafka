#!/usr/bin/env python3
"""
Sales Analytics Dashboard
Streamlit dashboard for visualizing sales data from PostgreSQL
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from datetime import datetime, timedelta
import time
import logging
import os
from dotenv import load_dotenv
load_dotenv()




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sales',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD'), 
    'port': '5050'
}

@st.cache_resource  # Cache for database connections
def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_sales_data():
    """Load sales data from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        # Load main sales data
        query = """
        SELECT * FROM sales_data 
        ORDER BY timestamp DESC 
        LIMIT 1000
        """
        df = pd.read_sql(query, conn)
        
        # Load summary data
        daily_summary = pd.read_sql("SELECT * FROM daily_sales_summary", conn)
        regional_summary = pd.read_sql("SELECT * FROM regional_performance", conn)
        product_summary = pd.read_sql("SELECT * FROM product_performance", conn)
        
        conn.close()
        
        return df, daily_summary, regional_summary, product_summary
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        conn.close()
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def display_kpi_metrics(df):
    """Display KPI metrics"""
    if df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df['total_price'].sum()
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta=None
        )
    
    with col2:
        total_orders = len(df)
        st.metric(
            label="📦 Total Orders",
            value=f"{total_orders:,}",
            delta=None
        )
    
    with col3:
        avg_order_value = df['total_price'].mean()
        st.metric(
            label="📈 Avg Order Value",
            value=f"${avg_order_value:,.2f}",
            delta=None
        )
    
    with col4:
        unique_customers = df['customer_id'].nunique()
        st.metric(
            label="👥 Unique Customers",
            value=f"{unique_customers:,}",
            delta=None
        )

def plot_revenue_by_region(regional_summary):
    """Plot revenue by region"""
    if regional_summary.empty:
        return
    
    fig = px.bar(
        regional_summary,
        x='region',
        y='total_revenue',
        title='Revenue by Region',
        color='total_revenue',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Total Revenue ($)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_top_products(product_summary, top_n=10):
    """Plot top products by revenue"""
    if product_summary.empty:
        return
    
    top_products = product_summary.head(top_n)
    
    fig = px.bar(
        top_products,
        x='product',
        y='total_revenue',
        title=f'Top {top_n} Products by Revenue',
        color='total_revenue',
        color_continuous_scale='plasma'
    )
    
    fig.update_layout(
        xaxis_title="Product",
        yaxis_title="Total Revenue ($)",
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_sales_trend(daily_summary):
    """Plot sales trend over time"""
    if daily_summary.empty:
        return
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Revenue Trend', 'Daily Orders Trend'),
        vertical_spacing=0.1
    )
    
    # Revenue trend
    fig.add_trace(
        go.Scatter(
            x=daily_summary['sale_date'],
            y=daily_summary['total_revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Orders trend
    fig.add_trace(
        go.Scatter(
            x=daily_summary['sale_date'],
            y=daily_summary['total_orders'],
            mode='lines+markers',
            name='Orders',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="Sales Trends Over Time",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_product_quantity_distribution(df):
    """Plot product quantity distribution"""
    if df.empty:
        return
    
    fig = px.histogram(
        df,
        x='quantity',
        title='Product Quantity Distribution',
        nbins=20,
        color_discrete_sequence=['lightblue']
    )
    
    fig.update_layout(
        xaxis_title="Quantity",
        yaxis_title="Frequency",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main dashboard function"""
    st.title("📊 Sales Analytics Dashboard")
    st.markdown("---")
    
    # Add refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load data
    df, daily_summary, regional_summary, product_summary = load_sales_data()
    
    if df.empty:
        st.warning("No data available. Please check your database connection and ensure data is being loaded.")
        return
    
    # Display KPI metrics
    st.subheader("📈 Key Performance Indicators")
    display_kpi_metrics(df)
    
    st.markdown("---")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Regional Performance")
        plot_revenue_by_region(regional_summary)
    
    with col2:
        st.subheader("🏆 Top Products")
        plot_top_products(product_summary, top_n=8)
    
    st.markdown("---")
    
    # Sales trends
    st.subheader("📈 Sales Trends")
    plot_sales_trend(daily_summary)
    
    # Additional charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📦 Quantity Distribution")
        plot_product_quantity_distribution(df)
    
    with col4:
        st.subheader("📋 Recent Sales Data")
        recent_data = df.head(10)[['order_id', 'product', 'quantity', 'total_price', 'region', 'timestamp']]
        recent_data['timestamp'] = pd.to_datetime(recent_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(recent_data, use_container_width=True)

if __name__ == "__main__":
    main() 