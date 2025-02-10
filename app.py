import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

def fetch_nfl_data(api_key):
    """Fetch NFL team data from RapidAPI"""
    url = "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "nfl-api-data.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Print response details for debugging
        st.sidebar.write(f"Status Code: {response.status_code}")
        st.sidebar.write(f"Response Size: {len(response.content)} bytes")
        
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e, 'response'):
            st.error(f"Response Content: {e.response.text}")
        return None

def process_nfl_data(data):
    """Process NFL data into a pandas DataFrame"""
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    
    # Rename columns to match our display format
    column_mapping = {
        'team_name': 'Team',
        'team_city': 'City',
        'team_conference': 'Conference',
        'team_division': 'Division'
    }
    
    df = df.rename(columns=column_mapping)
    return df

def highlight_conference(val, conference):
    """Return CSS style for conference"""
    colors = {
        'AFC': 'background-color: #ffcdd2',
        'NFC': 'background-color: #c8e6c9'
    }
    return colors.get(val, '')

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Add API Key input in sidebar
    api_key = st.sidebar.text_input(
        "Enter your RapidAPI Key",
        value="e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c",  # Default key from screenshot
        type="password"
    )
    
    if not api_key:
        st.warning("Please enter your RapidAPI key in the sidebar to fetch NFL data.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Teams", "Zodiac Calculator"])
    
    with tab1:
        # Fetch data using the provided API key
        with st.spinner("Loading NFL team data..."):
            data = fetch_nfl_data(api_key)
            
            if not data:
                st.error("Failed to fetch data. Please check your API key and try again.")
                return
            
            # Process data
            df = process_nfl_data(data)
            
            if df.empty:
                st.error("No data available to display")
                return
            
            # Create columns for layout
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.subheader("Filters")
                
                # Conference filter
                conferences = ['All Conferences'] + sorted(df['Conference'].unique().tolist())
                selected_conference = st.selectbox('Conference', conferences)
                
                # Division filter
                divisions = ['All Divisions'] + sorted(df['Division'].unique().tolist())
                selected_division = st.selectbox('Division', divisions)
                
                # Search box
                search = st.text_input("Search teams")
            
            with col2:
                # Apply filters
                filtered_df = df.copy()
                
                if selected_conference != 'All Conferences':
                    filtered_df = filtered_df[filtered_df['Conference'] == selected_conference]
                
                if selected_division != 'All Divisions':
                    filtered_df = filtered_df[filtered_df['Division'] == selected_division]
                
                # Apply search
                if search:
                    search_lower = search.lower()
                    mask = (
                        filtered_df['Team'].str.lower().str.contains(search_lower, na=False) |
                        filtered_df['City'].str.lower().str.contains(search_lower, na=False)
                    )
                    filtered_df = filtered_df[mask]
                
                # Style the dataframe
                styled_df = filtered_df.style.applymap(
                    lambda x: highlight_conference(x, selected_conference),
                    subset=['Conference']
                )
                
                # Display results
                st.write(f"Showing {len(filtered_df)} teams")
                st.dataframe(styled_df, hide_index=True)
                
                # Export functionality
                if st.button("Export to CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"nfl_teams_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()
