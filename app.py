import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# RapidAPI Configuration
RAPIDAPI_KEY = "e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c"
RAPIDAPI_HOST = "nfl-football-api.p.rapidapi.com"
API_URL = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo"

def fetch_nfl_data(api_key):
    """Fetch NFL data from RapidAPI"""
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": api_key
    }
    
    try:
        # Add debug information
        st.sidebar.write("Making API request...")
        st.sidebar.write("Headers:", {k: '***' if 'key' in k.lower() else v for k, v in headers.items()})
        
        response = requests.get(API_URL, headers=headers)
        
        # Print response details for debugging
        st.sidebar.write(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            st.error(f"Response Content: {response.text}")
            return None
            
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        if hasattr(e, 'response'):
            st.error(f"Response Content: {e.response.text if e.response else 'No response content'}")
        return None

def process_nfl_data(data):
    """Process NFL data into a pandas DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        # First, let's examine the structure of the data
        st.sidebar.write("Data structure received:", type(data))
        
        # Convert the data to a DataFrame based on its structure
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dictionary, we might need to extract the relevant part
            # We'll print the keys to help understand the structure
            st.sidebar.write("Available data keys:", data.keys())
            # For now, we'll try to convert the whole dict to a dataframe
            df = pd.DataFrame([data])
        else:
            st.error("Unexpected data format received")
            st.write("Raw data:", data)
            return pd.DataFrame()
        
        # Display the columns we received
        st.sidebar.write("Columns in data:", df.columns.tolist())
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Raw data received:", data)
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
    
    # Fetch data using the provided API key
    with st.spinner("Loading NFL data..."):
        data = fetch_nfl_data(api_key)
        
        if not data:
            return
        
        # Process data
        df = process_nfl_data(data)
        
        if df.empty:
            return
        
        # Display the raw data for now so we can see what we're working with
        st.write("### Raw NFL Data")
        st.write(df)
        
        # Once we see the data structure, we can add more specific formatting and filtering options

if __name__ == "__main__":
    main()
