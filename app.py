import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time

# RapidAPI Configuration
RAPIDAPI_KEY = "e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c"
RAPIDAPI_HOST = "nfl-football-api.p.rapidapi.com"

def fetch_nfl_data():
    """Fetch NFL data from RapidAPI with rate limiting and error handling"""
    base_url = "https://nfl-football-api.p.rapidapi.com"
    endpoints = [
        "/nfl-leagueinfo",
        "/api/v1/teams",
        "/teams",
        "/v1/teams"
    ]
    
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY
    }
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        st.sidebar.markdown(f"Trying endpoint: {endpoint}")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit exceeded
                    if attempt < max_retries - 1:
                        st.warning(f"Rate limit exceeded. Waiting {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        st.error("Rate limit exceeded. Please try again later.")
                elif response.status_code == 403:
                    st.error("Access forbidden. Please check the API subscription status.")
                    return None
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Request error: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                return None
            
    return None

[Rest of the code remains exactly the same as before, just change the main() function to remove the API key input]

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Teams", "Zodiac Calculator"])
    
    with tab1:
        # Fetch and display team data
        with st.spinner("Loading NFL data..."):
            data = fetch_nfl_data()
            
            if data:
                df = process_nfl_data(data)
                
                if not df.empty:
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
    
    with tab2:
        # Zodiac Calculator
        st.subheader("Zodiac Sign Calculator")
        
        default_date = date(1988, 1, 1)
        birth_date = st.date_input(
            "Enter birth date",
            value=default_date,
            format="MM/DD/YYYY"
        )
        
        if birth_date:
            zodiac_sign = get_zodiac_sign(birth_date)
            compatible_signs = get_compatible_signs(zodiac_sign)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"### Your Zodiac Sign: {zodiac_sign}")
                st.write("### Compatible Signs:")
                for sign in compatible_signs:
                    st.write(f"- {sign}")
            
            with col2:
                characteristics = {
                    'Aries': ['Leadership', 'Energy', 'Adventure'],
                    'Taurus': ['Reliability', 'Patience', 'Determination'],
                    'Gemini': ['Adaptability', 'Communication', 'Curiosity'],
                    'Cancer': ['Intuition', 'Emotional Intelligence', 'Nurturing'],
                    'Leo': ['Confidence', 'Creativity', 'Enthusiasm'],
                    'Virgo': ['Analysis', 'Practicality', 'Attention to Detail'],
                    'Libra': ['Diplomacy', 'Balance', 'Grace'],
                    'Scorpio': ['Passion', 'Intuition', 'Power'],
                    'Sagittarius': ['Optimism', 'Freedom', 'Adventure'],
                    'Capricorn': ['Ambition', 'Discipline', 'Patience'],
                    'Aquarius': ['Innovation', 'Independence', 'Originality'],
                    'Pisces': ['Empathy', 'Creativity', 'Intuition']
                }
                
                st.write("### Your Characteristics:")
                for trait in characteristics.get(zodiac_sign, []):
                    st.write(f"- {trait}")

if __name__ == "__main__":
    main()
