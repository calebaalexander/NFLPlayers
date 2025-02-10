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
        # Add debug information
        st.sidebar.write("Making API request...")
        st.sidebar.write("Headers:", {k: '***' if 'key' in k.lower() else v for k, v in headers.items()})
        
        response = requests.get(url, headers=headers)
        
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
        df = pd.DataFrame(data)
        
        # Rename columns to match our display format
        column_mapping = {
            'team_name': 'Team',
            'team_city': 'City',
            'team_conference': 'Conference',
            'team_division': 'Division'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Fill any NA values
        df['Team'] = df['Team'].fillna('Unknown')
        df['Conference'] = df['Conference'].fillna('Unknown')
        df['Division'] = df['Division'].fillna('Unknown')
        df['City'] = df['City'].fillna('Unknown')
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Raw data received:", data)
        return pd.DataFrame()

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
    st.sidebar.title("API Configuration")
    api_key = st.sidebar.text_input(
        "Enter your RapidAPI Key",
        value="e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c",
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
                return
            
            # Process data
            df = process_nfl_data(data)
            
            if df.empty:
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
