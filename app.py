import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# RapidAPI Configuration
RAPIDAPI_KEY = "e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c"
RAPIDAPI_HOST = "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
API_URL = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"

def get_nfl_data():
    """Fetch NFL data from Tank01 API"""
    url = f"{API_URL}/getNFLDFS?date=20250119"
    
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY
    }
    
    try:
        st.sidebar.write("Making API request...")
        st.sidebar.write("URL:", url)
        st.sidebar.write("Headers:", {k: '***' if 'key' in k.lower() else v for k, v in headers.items()})
        
        response = requests.get(url, headers=headers)
        
        # Print response details for debugging
        st.sidebar.write(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {str(e)}")
        return None

def get_nfl_teams():
    """Fetch NFL teams from Tank01 API"""
    url = f"{API_URL}/getNFLTeams"
    
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def process_data(data):
    """Process NFL data into DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        # Check the structure of the data
        st.sidebar.write("Data structure:", type(data))
        if isinstance(data, dict) and 'body' in data:
            data = data['body']
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            st.error(f"Unexpected data type: {type(data)}")
            return pd.DataFrame()
        
        # Show available columns
        st.sidebar.write("Available columns:", df.columns.tolist())
        
        # Fill missing values
        df = df.fillna('Unknown')
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Raw data:", data)
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Create tabs
    tab1, tab2 = st.tabs(["NFL Data", "Zodiac Calculator"])
    
    with tab1:
        # Fetch NFL data
        with st.spinner("Loading NFL data..."):
            data = get_nfl_data()
            teams_data = get_nfl_teams()
            
            if data or teams_data:
                # Process main data
                df = process_data(data)
                teams_df = process_data(teams_data)
                
                # Display raw data for inspection
                st.write("### Raw Data Structure")
                if not df.empty:
                    st.write("Main Data Columns:", df.columns.tolist())
                if not teams_df.empty:
                    st.write("Teams Data Columns:", teams_df.columns.tolist())
                
                # Display the data
                if not df.empty:
                    st.write("### NFL Data")
                    st.dataframe(df)
                
                if not teams_df.empty:
                    st.write("### NFL Teams")
                    st.dataframe(teams_df)
                
                # Export functionality
                if st.button("Export to CSV"):
                    csv = df.to_csv(index=False) if not df.empty else teams_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"nfl_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    with tab2:
        # [Zodiac Calculator code remains the same...]
        st.write("Zodiac Calculator functionality available in the next tab.")

if __name__ == "__main__":
    main()
