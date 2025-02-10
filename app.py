import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# RapidAPI Configuration
RAPIDAPI_KEY = "e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c"
RAPIDAPI_HOST = "nfl-api-data.p.rapidapi.com"
API_URL = "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"

# Cache data to avoid multiple API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_nfl_data():
    """Fetch NFL team data from RapidAPI"""
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
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

def calculate_age(birth_date):
    """Calculate age from birth date, handling invalid dates"""
    try:
        birth_date = pd.to_datetime(birth_date)
        today = pd.Timestamp.now()
        age = (today - birth_date).days / 365.25
        return int(age) if pd.notnull(age) else None
    except:
        return None

def process_nfl_data(data):
    """Process NFL data into a pandas DataFrame"""
    if not data or not isinstance(data, list):
        return pd.DataFrame()
    
    # Create DataFrame from the API response
    df = pd.DataFrame(data)
    
    # Rename columns to match our display format
    column_mapping = {
        'team_name': 'Team',
        'team_city': 'City',
        'team_conference': 'Conference',
        'team_division': 'Division',
        'team_logo_url': 'Logo URL'
    }
    
    df = df.rename(columns=column_mapping)
    
    # Fill any NA values
    df['Team'] = df['Team'].fillna('Unknown')
    df['Conference'] = df['Conference'].fillna('Unknown')
    df['Division'] = df['Division'].fillna('Unknown')
    df['City'] = df['City'].fillna('Unknown')
    
    return df

def highlight_compatible_signs(val, compatible_signs):
    """Return CSS style if zodiac sign is compatible"""
    return 'background-color: yellow' if val in compatible_signs else ''

def highlight_conference(val, conference):
    """Return CSS style for conference"""
    colors = {
        'AFC': 'background-color: #ffcdd2',
        'NFC': 'background-color: #c8e6c9'
    }
    return colors.get(val, '')

def main():
    st.set_page_config(
        page_title="NFL Teams Explorer",
        page_icon="🏈",
        layout="wide"
    )

    st.title("🏈 NFL Teams Explorer")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Teams", "Zodiac Calculator"])
    
    with tab1:
        # Fetch data from RapidAPI
        with st.spinner("Loading NFL team data..."):
            data = fetch_nfl_data()
        
        if not data:
            st.error("Failed to fetch data from the API")
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
            st.dataframe(
                styled_df,
                hide_index=True,
                column_config={
                    "Logo URL": st.column_config.ImageColumn("Team Logo")
                }
            )
            
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

if __name__ == "__main__":
    main()
