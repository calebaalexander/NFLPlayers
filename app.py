import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import json

def fetch_nfl_data(api_key):
    """Fetch NFL data from RapidAPI"""
    # Try different endpoints
    endpoints = [
        "/nfl-leagueinfo",
        "/api/v1/teams",
        "/teams",
        "/v1/teams"
    ]
    
    base_url = "https://nfl-football-api.p.rapidapi.com"
    
    headers = {
        "X-RapidAPI-Host": "nfl-football-api.p.rapidapi.com",
        "X-RapidAPI-Key": api_key,
        "Accept": "application/json"
    }
    
    # Try each endpoint
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        st.sidebar.markdown(f"Trying endpoint: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.sidebar.error(f"Failed with status {response.status_code}")
                if response.text:
                    st.sidebar.write("Response:", response.text)
                
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Error with endpoint {endpoint}: {str(e)}")
    
    return None

def get_zodiac_sign(birth_date):
    """Calculate zodiac sign from birth date"""
    try:
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date)
        
        month = birth_date.month
        day = birth_date.day
        
        zodiac_dates = [
            (120, 'Capricorn'),  # Dec 22 - Jan 19
            (219, 'Aquarius'),   # Jan 20 - Feb 18
            (320, 'Pisces'),     # Feb 19 - Mar 20
            (420, 'Aries'),      # Mar 21 - Apr 19
            (521, 'Taurus'),     # Apr 20 - May 20
            (621, 'Gemini'),     # May 21 - Jun 20
            (723, 'Cancer'),     # Jun 21 - Jul 22
            (823, 'Leo'),        # Jul 23 - Aug 22
            (923, 'Virgo'),      # Aug 23 - Sep 22
            (1023, 'Libra'),     # Sep 23 - Oct 22
            (1122, 'Scorpio'),   # Oct 23 - Nov 21
            (1222, 'Sagittarius'),# Nov 22 - Dec 21
            (1232, 'Capricorn')  # Dec 22 - Dec 31
        ]
        
        date_num = month * 100 + day
        
        for cutoff, sign in zodiac_dates:
            if date_num <= cutoff:
                return sign
        return 'Capricorn'
    except:
        return None

def get_compatible_signs(zodiac):
    """Return most compatible zodiac signs"""
    compatibility = {
        'Aries': ['Leo', 'Sagittarius', 'Gemini'],
        'Taurus': ['Virgo', 'Capricorn', 'Cancer'],
        'Gemini': ['Libra', 'Aquarius', 'Aries'],
        'Cancer': ['Scorpio', 'Pisces', 'Taurus'],
        'Leo': ['Aries', 'Sagittarius', 'Gemini'],
        'Virgo': ['Taurus', 'Capricorn', 'Cancer'],
        'Libra': ['Gemini', 'Aquarius', 'Leo'],
        'Scorpio': ['Cancer', 'Pisces', 'Virgo'],
        'Sagittarius': ['Aries', 'Leo', 'Libra'],
        'Capricorn': ['Taurus', 'Virgo', 'Pisces'],
        'Aquarius': ['Gemini', 'Libra', 'Sagittarius'],
        'Pisces': ['Cancer', 'Scorpio', 'Capricorn']
    }
    return compatibility.get(zodiac, [])

def process_nfl_data(data):
    """Process NFL data into a pandas DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dictionary, we might need to extract the relevant part
            if 'teams' in data:
                df = pd.DataFrame(data['teams'])
            else:
                df = pd.DataFrame([data])
        else:
            st.error(f"Unexpected data type: {type(data)}")
            return pd.DataFrame()
        
        # Rename columns if needed
        column_mapping = {
            'team_name': 'Team',
            'team_city': 'City',
            'team_conference': 'Conference',
            'team_division': 'Division',
            'name': 'Team',
            'city': 'City',
            'conference': 'Conference',
            'division': 'Division'
        }
        
        # Rename only the columns that exist
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Raw data:", data)
        return pd.DataFrame()

def highlight_conference(val, conference):
    """Return CSS style for conference"""
    colors = {
        'AFC': 'background-color: #ffcdd2',
        'NFC': 'background-color: #c8e6c9'
    }
    return colors.get(val, '')

def display_zodiac_calculator():
    """Display the zodiac calculator section"""
    st.subheader("Zodiac Sign Calculator")
    
    # Add date input for zodiac calculation
    default_date = date(1988, 1, 1)
    user_date = st.date_input(
        "Enter your birth date",
        value=default_date,
        format="MM/DD/YYYY"
    )
    
    # Calculate and display zodiac sign
    user_zodiac = get_zodiac_sign(user_date)
    
    if user_zodiac:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"### Your Zodiac Sign: {user_zodiac}")
            
            # Display compatible signs
            compatible_signs = get_compatible_signs(user_zodiac)
            st.write("### Compatible Signs:")
            for sign in compatible_signs:
                st.write(f"- {sign}")
        
        with col2:
            # Display zodiac characteristics
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
            for trait in characteristics.get(user_zodiac, []):
                st.write(f"- {trait}")

def display_teams_explorer(api_key):
    """Display the teams explorer section"""
    # Fetch data using the provided API key
    with st.spinner("Loading NFL data..."):
        data = fetch_nfl_data(api_key)
        
        if not data:
            st.error("""
            Failed to fetch data. Please check:
            1. Your API key is correct
            2. You have an active subscription to this API
            3. The subscription has been activated (can take a few minutes)
            """)
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
    
    # Add subscription verification checklist
    st.sidebar.markdown("""
    ### Subscription Checklist:
    1. ✓ Visit RapidAPI NFL Football API page
    2. ✓ Subscribe to an appropriate tier
    3. ✓ Wait a few minutes for subscription to activate
    4. ✓ Verify API key matches your RapidAPI account
    """)
    
    if not api_key:
        st.warning("Please enter your RapidAPI key in the sidebar to fetch NFL data.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Teams", "Zodiac Calculator"])
    
    with tab1:
        display_teams_explorer(api_key)
    
    with tab2:
        display_zodiac_calculator()

if __name__ == "__main__":
    main()
