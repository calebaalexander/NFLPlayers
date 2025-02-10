import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

def fetch_nfl_data(api_key):
    """Fetch NFL data from RapidAPI"""
    url = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo"
    
    headers = {
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Print complete response details for debugging
        st.sidebar.write(f"Response Status: {response.status_code}")
        st.sidebar.write(f"Response Headers: {dict(response.headers)}")
        st.sidebar.write(f"Response Content: {response.text[:1000] if response.text else 'No content'}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e, 'response'):
            st.error(f"Response Content: {e.response.text if e.response else 'No response content'}")
        return None

def process_nfl_data(data):
    """Process NFL data into a pandas DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        # Print raw data structure for debugging
        st.sidebar.write("Raw data type:", type(data))
        st.sidebar.write("Raw data preview:", str(data)[:1000])
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dictionary, convert it to a DataFrame
            df = pd.DataFrame([data])
        else:
            st.error(f"Unexpected data type: {type(data)}")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Raw data:", data)
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Add API Key input in sidebar
    st.sidebar.title("API Configuration")
    api_key = st.sidebar.text_input(
        "Enter your RapidAPI Key",
        value="e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c",
        type="password"
    )
    
    if not api_key:
        st.warning("Please enter your RapidAPI key in the sidebar to fetch NFL data.")
        return
    
    # Show current API configuration
    st.sidebar.write("Current API Configuration:")
    st.sidebar.json({
        "url": "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo",
        "host": "nfl-football-api.p.rapidapi.com"
    })
    
    # Fetch data using the provided API key
    with st.spinner("Loading NFL data..."):
        data = fetch_nfl_data(api_key)
        
        if data:
            df = process_nfl_data(data)
            if not df.empty:
                st.write("### NFL Data")
                st.dataframe(df)
            else:
                st.error("No data available to display")
        else:
            st.error("Failed to fetch data. Please verify your API subscription and key.")

if __name__ == "__main__":
    main()
