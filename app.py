import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time

# RapidAPI Configuration
RAPIDAPI_KEY = "e76e6d59aamshd574b36f1e312ap1a642ejsn4a367f21a64c"
RAPIDAPI_HOST = "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"

# Cache data to avoid rate limits
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_nfl_data():
    """Fetch NFL data from Tank01 API with rate limiting"""
    base_url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
    
    # Headers
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    
    # Add delay between requests
    delay = 1  # seconds
    max_retries = 3
    
    endpoints = [
        "/getTeamListing",  # Try different team endpoint
        "/getNFLTeamInfo",  # Another team endpoint
        "/getNFLTeams"      # Original endpoint
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        st.sidebar.write(f"Trying endpoint: {endpoint}")
        
        for attempt in range(max_retries):
            try:
                time.sleep(delay)  # Rate limiting delay
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Exponential backoff
                        st.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        st.error("Rate limit exceeded. Please try again later.")
                elif response.status_code == 403:
                    st.error("Unauthorized access. Please check your API subscription.")
                    break  # Don't retry on auth errors
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                break
    
    return None

def process_data(data):
    """Process NFL data into DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        if isinstance(data, dict):
            if 'body' in data:
                data = data['body']
            elif 'teams' in data:
                data = data['teams']
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            st.error(f"Unexpected data type: {type(data)}")
            return pd.DataFrame()
        
        # Fill missing values
        df = df.fillna('Unknown')
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return pd.DataFrame()

def get_zodiac_sign(birth_date):
    """Calculate zodiac sign from birth date"""
    try:
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date)
        
        month = birth_date.month
        day = birth_date.day
        
        zodiac_dates = [
            (120, 'Capricorn'),   # Dec 22 - Jan 19
            (219, 'Aquarius'),    # Jan 20 - Feb 18
            (320, 'Pisces'),      # Feb 19 - Mar 20
            (420, 'Aries'),       # Mar 21 - Apr 19
            (521, 'Taurus'),      # Apr 20 - May 20
            (621, 'Gemini'),      # May 21 - Jun 20
            (723, 'Cancer'),      # Jun 21 - Jul 22
            (823, 'Leo'),         # Jul 23 - Aug 22
            (923, 'Virgo'),       # Aug 23 - Sep 22
            (1023, 'Libra'),      # Sep 23 - Oct 22
            (1122, 'Scorpio'),    # Oct 23 - Nov 21
            (1222, 'Sagittarius'),# Nov 22 - Dec 21
            (1232, 'Capricorn')   # Dec 22 - Dec 31
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

def main():
    st.set_page_config(page_title="NFL Teams Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Teams Explorer")
    
    # Create tabs
    tab1, tab2 = st.tabs(["NFL Data", "Zodiac Calculator"])
    
    with tab1:
        # Add refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
            
        # Fetch NFL data
        with st.spinner("Loading NFL data..."):
            data = get_nfl_data()
            
            if data:
                df = process_data(data)
                
                if not df.empty:
                    # Create layout
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.subheader("Filters")
                        
                        # Search box
                        search = st.text_input("Search teams")
                        
                        # Dynamic filters based on data
                        filters = {}
                        for col in df.columns:
                            if df[col].nunique() < 30:  # Only add filter for columns with reasonable unique values
                                values = ['All'] + sorted(df[col].unique().tolist())
                                filters[col] = st.selectbox(f'Filter by {col}', values)
                    
                    with col2:
                        # Apply filters
                        filtered_df = df.copy()
                        
                        for col, value in filters.items():
                            if value != 'All':
                                filtered_df = filtered_df[filtered_df[col] == value]
                        
                        # Apply search
                        if search:
                            search_lower = search.lower()
                            mask = filtered_df.astype(str).apply(
                                lambda x: x.str.lower().str.contains(search_lower, na=False)
                            ).any(axis=1)
                            filtered_df = filtered_df[mask]
                        
                        # Display results
                        st.write(f"Showing {len(filtered_df)} teams")
                        st.dataframe(filtered_df)
                        
                        # Export functionality
                        if st.button("Export to CSV"):
                            csv = filtered_df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"nfl_data_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
    
    with tab2:
        st.subheader("Zodiac Sign Calculator")
        
        # Date input
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
