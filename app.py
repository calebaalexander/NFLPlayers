import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

def fetch_nfl_data(api_key):
    """Fetch NFL team data from RapidAPI"""
    url = "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"
    
    headers = {
        "x-rapidapi-host": "nfl-api-data.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    
    try:
        # Print the request details for debugging
        st.sidebar.write("Making API request...")
        st.sidebar.write(f"URL: {url}")
        st.sidebar.write("Headers:", {k: '***' if 'key' in k.lower() else v for k, v in headers.items()})
        
        response = requests.get(url, headers=headers)
        
        # Print response details for debugging
        st.sidebar.write(f"Response Status: {response.status_code}")
        if response.status_code != 200:
            st.sidebar.write("Response Content:", response.text)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e, 'response'):
            st.error(f"Response Content: {e.response.text if e.response else 'No response content'}")
        return None

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Add API Key input in sidebar with clear instructions
    st.sidebar.title("API Configuration")
    st.sidebar.markdown("""
    To use this app:
    1. Go to RapidAPI
    2. Subscribe to the NFL API
    3. Copy your API key
    4. Paste it below
    """)
    
    api_key = st.sidebar.text_input("Enter your RapidAPI Key", type="password")
    
    if not api_key:
        st.warning("Please enter your RapidAPI key in the sidebar to fetch NFL data.")
        return
        
    # Rest of your code stays the same...
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Teams", "Zodiac Calculator"])
    
    with tab1:
        # Fetch data using the provided API key
        with st.spinner("Loading NFL team data..."):
            data = fetch_nfl_data(api_key)
            
            if not data:
                return
                
            # Process and display data...
            st.write("Data fetched successfully!")
            st.write(data)  # For debugging - remove in production

if __name__ == "__main__":
    main()
