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
from plotly.subplots import make_subplots
from utils import update_prices, format_price, load_price_history

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



# Main app - Get current date/time for title
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%d/%m -%y | %H:%M:%S")
st.title(f"📊 :red[AKT] & :orange[SPICE] PRICE | {formatted_datetime}")
st.caption("Real-time cryptocurrency prices from CoinGecko API")

# Fetch prices on first run or if prices are None
if st.session_state.prices is None:
    update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE)

# Auto-refresh logic
if datetime.now() >= st.session_state.next_refresh:
    update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE)



# Load historical data and create charts
df = load_price_history(DATA_FILE)
if not df.empty:
    # Create tabs for USD and SEK charts
    tab1, tab2 = st.tabs(["USD Prices", "SEK Prices"])
    
    with tab1:
        
        # Create two columns for separate charts
        col_akt, col_spice = st.columns(2)
        
        with col_akt:
            st.markdown("**AKT Price (USD)**")
            # Create Plotly chart for AKT USD
            fig_akt = go.Figure()
            fig_akt.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['akt_usd'],
                mode='lines+markers',
                line=dict(color='#FF0000', width=2),
                name='AKT'
            ))
            fig_akt.update_layout(
                yaxis=dict(
                    tickformat=".2f",
                    title="Price (USD)"
                ),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_akt, use_container_width=True)
        
        with col_spice:
            st.markdown("**SPICE Price (USD)**")
            # Create Plotly chart for SPICE USD
            fig_spice = go.Figure()
            fig_spice.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['spice_usd'],
                mode='lines+markers',
                line=dict(color='#FFA500', width=2),
                name='SPICE'
            ))
            fig_spice.update_layout(
                yaxis=dict(
                    tickformat=".6f",  # Force 6 decimal places
                    title="Price (USD)"
                ),
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
            # Create Plotly chart for AKT SEK
            fig_akt = go.Figure()
            fig_akt.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['akt_sek'],
                mode='lines+markers',
                line=dict(color='#FF0000', width=2),
                name='AKT'
            ))
            fig_akt.update_layout(
                yaxis=dict(
                    tickformat=".2f",
                    title="Price (SEK)"
                ),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_akt, use_container_width=True)
        
        with col_spice:
            st.markdown("**SPICE Price (SEK)**")
            # Create Plotly chart for SPICE SEK
            fig_spice = go.Figure()
            fig_spice.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['spice_sek'],
                mode='lines+markers',
                line=dict(color='#FFA500', width=2),
                name='SPICE'
            ))
            fig_spice.update_layout(
                yaxis=dict(
                    tickformat=".6f",  # Force 6 decimal places
                    title="Price (SEK)"
                ),
                xaxis_title="Time",
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig_spice, use_container_width=True)
        
        # Display raw data
        with st.expander("View SEK Data"):
            # Format SPICE prices to 6 decimals for display
            display_df = df.copy()
            display_df['spice_sek'] = display_df['spice_sek'].apply(lambda x: f"{x:.6f}")
            display_df = display_df[['timestamp', 'akt_sek', 'spice_sek']].rename(columns={
                'timestamp': 'Timestamp',
                'akt_sek': 'AKT (SEK)',
                'spice_sek': 'SPICE (SEK)'
            }).set_index('Timestamp').sort_index(ascending=False)
            st.dataframe(display_df, height=300)
else:
    st.info("No historical data available yet. Data will be saved after each refresh.")


# Create layout for price cards
col1, col2 = st.columns(2)


# AKT Price Card
with col1:
    st.subheader(":red[$AKT]")
    if st.session_state.prices and 'akt' in st.session_state.prices:
        akt = st.session_state.prices['akt']
        st.metric("USD Price", format_price(akt['usd'], 'usd'), border=True)
        st.metric("SEK Price", format_price(akt['sek'], 'sek'), border=True)
    else:
        st.warning("AKT price data not available")

# SPICE Price Card
with col2:
    st.subheader(":orange[$SPICE]")
    if st.session_state.prices and 'spice' in st.session_state.prices:
        spice = st.session_state.prices['spice']
        st.metric("USD Price", format_price(spice['usd'], 'usd', True), border=True)
        st.metric("SEK Price", format_price(spice['sek'], 'sek', True), border=True)
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
    # Format SPICE prices to 6 decimals for display
    display_df = df.copy()
    display_df['spice_usd'] = display_df['spice_usd'].apply(lambda x: f"{x:.6f}")
    display_df = display_df[['timestamp', 'akt_usd', 'spice_usd']].rename(columns={
        'timestamp': 'Timestamp',
        'akt_usd': 'AKT (USD)',
        'spice_usd': 'SPICE (USD)'
    }).set_index('Timestamp').sort_index(ascending=False)
    st.dataframe(display_df, height=300)


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