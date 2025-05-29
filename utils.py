import requests
from datetime import datetime, timedelta
import csv
import time
import streamlit as st
import pandas as pd

def fetch_prices(API_URL, API_KEY, CURRENCIES, COINS):
    """Fetch current prices from CoinGecko API"""
    try:
        params = {
            'ids': ','.join(COINS),
            'vs_currencies': ','.join(CURRENCIES)
        }
        headers = {'x-cg-demo-api-key': API_KEY}
        
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return {
            'akt': {
                'usd': data['akash-network']['usd'],
                'sek': data['akash-network']['sek']
            },
            'spice': {
                'usd': data['spice-2']['usd'],
                'sek': data['spice-2']['sek']
            }
        }
    except Exception as e:
        st.error(f"Error fetching prices: {str(e)}")
        return None

def save_to_csv(prices, DATA_FILE, API_KEY):
    """Save prices to CSV file with metadata"""
    try:
        file_exists = DATA_FILE.exists()
        
        with open(DATA_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow([
                    'timestamp', 'akt_usd', 'akt_sek', 
                    'spice_usd', 'spice_sek', 'api_key'
                ])
            
            # Write data row
            writer.writerow([
                datetime.now().isoformat(),
                prices['akt']['usd'],
                prices['akt']['sek'],
                prices['spice']['usd'],
                prices['spice']['sek'],
                API_KEY[-4:]  # Store last 4 chars of API key for reference
            ])
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def update_prices(API_URL, API_KEY, CURRENCIES, COINS, DATA_FILE):
    """Update prices and refresh timer"""
    prices = fetch_prices(API_URL, API_KEY, CURRENCIES, COINS)
    if prices:
        st.session_state.prices = prices
        save_to_csv(prices, DATA_FILE, API_KEY)  # Save to CSV after successful fetch
    
    st.session_state.last_updated = datetime.now()
    st.session_state.next_refresh = datetime.now() + timedelta(minutes=5)
    st.session_state.last_refresh_time = time.time()
    st.rerun()

def format_price(price, currency, spice=False):
    """Format price based on currency"""
    # Always show 6 decimals for SPICE
    if spice:
        if currency == 'sek':
            return f"{price:,.6f} kr"
        else:  # usd
            return f"${price:,.6f}"
    
    # For AKT
    if currency == 'sek':
        return f"{price:,.2f} kr"
    elif currency == 'usd':
        return f"${price:,.2f}"
    return f"{price:,.8f}"

def load_price_history(DATA_FILE):
    """Load historical price data from CSV"""
    if not DATA_FILE.exists():
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Filter to last 24 hours (12 points per hour * 24 = 288 points)
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            df = df[df['timestamp'] >= twenty_four_hours_ago]
            df = df.sort_values('timestamp')
        return df
    except Exception as e:
        st.error(f"Error loading price history: {str(e)}")
        return pd.DataFrame()