import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import os
import pandas as pd
import csv
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go
from utils import update_prices, format_price, load_price_history, format_market_cap  # Added format_market_cap

load_dotenv()

API_KEY = os.getenv("API_KEY")

# Set page configuration
st.set_page_config(
    page_title="$AKT $SPICE Prices",
    page_icon="📊",
    layout="wide"
)

# API configuration
API_URL = "https://api.coingecko.com/api/v3/simple/price"
COINS = ['akash-network', 'spice-2']
CURRENCIES = ['usd', 'sek']

# File paths
DATA_FILE = Path("crypto_prices.csv")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# Initialize session state
if 'prices' not in st.session_state:
    st.session_state.prices = None
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = datetime.now()
if 'next_refresh' not in st.session_state:
    st.session_state.next_refresh = datetime.now() + timedelta(minutes=5)
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# ... (previous imports and setup code remains the same) ...

# Main app - Get current date/time for title
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%d/%m -%y | %H:%M:%S")
st.title(f"📊 :red[$AKT] & :orange[$SPICE] | {formatted_datetime}")
st.caption("Real-time cryptocurrency prices from CoinGecko API")

# Fetch prices on first run or if prices are None
if st.session_state.prices is None:
    update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE)

# Auto-refresh logic
if datetime.now() >= st.session_state.next_refresh:
    update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE)

# Load historical data and create charts
# ... (previous code remains the same) ...

# Load historical data and create charts
df = load_price_history(DATA_FILE)
if not df.empty:
    # Compute AKT/SPICE ratio
    df['akt_spice_ratio'] = df['akt_usd'] / df['spice_usd']
    
    # Create tabs for USD, SEK, and Ratio charts
    tab1, tab2, tab3 = st.tabs(["USD Prices", "SEK Prices", "AKT/SPICE Ratio"])
    
    with tab1:
        # Create two columns for separate charts
        col_akt, col_spice = st.columns(2)
        
        with col_akt:
            st.markdown("**AKT Price (USD)**")
            fig_akt = go.Figure()
            fig_akt.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['akt_usd'],
                mode='lines+markers',
                line=dict(color='#FF0000', width=2),
                name='AKT'
            ))
            fig_akt.update_layout(
                yaxis=dict(tickformat=".2f", title="Price (USD)"),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_akt, use_container_width=True)
        
        with col_spice:
            st.markdown("**SPICE Price (USD)**")
            fig_spice = go.Figure()
            fig_spice.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['spice_usd'],
                mode='lines+markers',
                line=dict(color='#FFA500', width=2),
                name='SPICE'
            ))
            fig_spice.update_layout(
                yaxis=dict(tickformat=".6f", title="Price (USD)"),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_spice, use_container_width=True)
    
    with tab2:
        # Create two columns for separate charts
        col_akt, col_spice = st.columns(2)
        
        with col_akt:
            st.markdown("**AKT Price (SEK)**")
            fig_akt = go.Figure()
            fig_akt.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['akt_sek'],
                mode='lines+markers',
                line=dict(color='#FF0000', width=2),
                name='AKT'
            ))
            fig_akt.update_layout(
                yaxis=dict(tickformat=".2f", title="Price (SEK)"),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_akt, use_container_width=True)
        
        with col_spice:
            st.markdown("**SPICE Price (SEK)**")
            fig_spice = go.Figure()
            fig_spice.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['spice_sek'],
                mode='lines+markers',
                line=dict(color='#FFA500', width=2),
                name='SPICE'
            ))
            fig_spice.update_layout(
                yaxis=dict(tickformat=".6f", title="Price (SEK)"),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_spice, use_container_width=True)
    
    with tab3:
        st.subheader("AKT/SPICE Price Ratio")
        st.markdown("**How much SPICE can one AKT buy?**")
        
        # Create Plotly chart for AKT/SPICE ratio
        fig_ratio = go.Figure()
        fig_ratio.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['akt_spice_ratio'],
            mode='lines+markers',
            line=dict(color='#00FF00', width=2),  # Green for ratio
            name='AKT/SPICE Ratio'
        ))
        fig_ratio.update_layout(
            yaxis=dict(
                title="Ratio (AKT per SPICE)",
                tickformat=",.0f"  # Format as whole numbers
            ),
            xaxis_title="Time",
            margin=dict(l=20, r=20, t=30, b=20),
            height=400
        )
        st.plotly_chart(fig_ratio, use_container_width=True)
        
        # Calculate and display current ratio
        if st.session_state.prices:
            akt_price = st.session_state.prices['akt']['usd']
            spice_price = st.session_state.prices['spice']['usd']
            
            # Avoid division by zero
            if spice_price > 0:
                current_ratio = akt_price / spice_price
                ratio_text = f"1 AKT = {current_ratio:,.0f} SPICE"
            else:
                current_ratio = 0
                ratio_text = "N/A (SPICE price unavailable)"
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Ratio", ratio_text)
            
            with col2:
                # Add interpretation guide
                st.markdown("""
                **Ratio Guide:**
                - **Higher ratio**: AKT is stronger relative to SPICE
                - **Lower ratio**: SPICE is stronger relative to AKT
                """)
        
        # Add ratio data table

else:
    st.info("No historical data available yet. Data will be saved after each refresh.")

# ... (rest of the code remains the same) ...

# ... (price cards and remaining code remains the same) ...

# Create layout for price cards - USD and SEK side-by-side
col1, col2 = st.columns(2)

# AKT Price Card
with col1:
    st.subheader(":red[$AKT]")
    if st.session_state.prices and 'akt' in st.session_state.prices:
        akt = st.session_state.prices['akt']
        
        # Create three columns for USD, SEK, and Market Cap
        col_usd, col_sek, col_mcap = st.columns(3)
        
        with col_usd:
            st.metric("USD", format_price(akt['usd'], 'usd'), border=True)
        
        with col_sek:
            st.metric("SEK", format_price(akt['sek'], 'sek'), border=True)
            
        with col_mcap:
            st.metric("Market Cap", format_market_cap(akt['market_cap']), border=True)
    else:
        st.warning("AKT price data not available")

# SPICE Price Card
with col2:
    st.subheader(":orange[$SPICE]")
    if st.session_state.prices and 'spice' in st.session_state.prices:
        spice = st.session_state.prices['spice']
        
        # Create three columns for USD, SEK, and Market Cap
        col_usd, col_sek, col_mcap = st.columns(3)
        
        with col_usd:
            st.metric("USD", format_price(spice['usd'], 'usd', True), border=True)
        
        with col_sek:
            st.metric("SEK", format_price(spice['sek'], 'sek', True), border=True)
            
        with col_mcap:
            st.metric("Market Cap", format_market_cap(spice['market_cap']), border=True)
    else:
        st.warning("SPICE price data not available")

# Refresh controls
st.text("")
refresh_col, time_col = st.columns([1, 3])

with refresh_col:
    if st.button("🔄 Refresh Prices Now!", type="primary", use_container_width=True):
        update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE)

# Calculate time until next refresh
time_left = st.session_state.next_refresh - datetime.now()
seconds_left = max(0, time_left.total_seconds())
minutes_left = int(seconds_left // 60)
remaining_seconds = int(seconds_left % 60)

# Display countdown timer
with time_col:
    progress = 1 - (seconds_left / 300)
    st.progress(progress, text=f"Next refresh in: {minutes_left}:{remaining_seconds:02d}")

# Last updated timestamp
last_update_str = st.session_state.last_updated.strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Last updated: {last_update_str}")

# Display raw data
with st.expander("View USD Data"):
    if not df.empty:
        display_df = df.copy()
        display_df['spice_usd'] = display_df['spice_usd'].apply(lambda x: f"{x:.6f}")
        display_df = display_df[['timestamp', 'akt_usd', 'spice_usd']].rename(columns={
            'timestamp': 'Timestamp',
            'akt_usd': 'AKT (USD)',
            'spice_usd': 'SPICE (USD)'
        }).set_index('Timestamp').sort_index(ascending=False)
        st.dataframe(display_df, height=300)
    else:
        st.info("No data available")

with st.expander("View SEK Data"):
    if not df.empty:
        display_df = df.copy()
        display_df['spice_sek'] = display_df['spice_sek'].apply(lambda x: f"{x:.6f}")
        display_df = display_df[['timestamp', 'akt_sek', 'spice_sek']].rename(columns={
            'timestamp': 'Timestamp',
            'akt_sek': 'AKT (SEK)',
            'spice_sek': 'SPICE (SEK)'
        }).set_index('Timestamp').sort_index(ascending=False)
        st.dataframe(display_df, height=300)
    else:
        st.info("No data available")

with st.expander("View Ratio Data"):
    ratio_df = df[['timestamp', 'akt_usd', 'spice_usd', 'akt_spice_ratio']].copy()
    ratio_df['akt_spice_ratio'] = ratio_df['akt_spice_ratio'].apply(lambda x: f"{x:,.0f}")
    ratio_df = ratio_df.rename(columns={
        'timestamp': 'Timestamp',
        'akt_usd': 'AKT Price (USD)',
        'spice_usd': 'SPICE Price (USD)',
        'akt_spice_ratio': 'AKT/SPICE Ratio'
    }).set_index('Timestamp').sort_index(ascending=False)
    st.dataframe(ratio_df, height=300)

# Add auto-rerun to update the timer every second
if seconds_left > 0:
    time.sleep(1)
    st.rerun()

# Add some visual styling
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #0e1117;
    border: 1px solid #2b2d31;
    border-radius: 10px;
    padding: 10px;
    min-height: 110px;  /* Ensure consistent height */
    display: flex;
    flex-direction: column;
    justify-content: center;
}
div[data-testid="stMetricLabel"] {
    color: #9e9e9e;
}
.st-emotion-cache-1v0mbdj {
    margin: 0 auto;
}
/* Improve chart titles */
h3 {
    font-size: 1.2rem !important;
    margin-bottom: 0.5rem !important;
}
/* Customize Plotly charts */
.js-plotly-plot .plotly .yaxis .tick text {
    font-size: 10px !important;
}
</style>
""", unsafe_allow_html=True)
