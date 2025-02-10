import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import re

# API Configuration
API_KEY = "6df769b0923f4826a1fbb8080e55cdf4"
API_URL = "https://api.sportsdata.io/v3/nfl/scores/json/PlayersByAvailable"

def parse_quota_message(message):
    """Extract time remaining from quota message"""
    try:
        match = re.search(r"(\d{2}):(\d{2}):(\d{2}):(\d{2})", message)
        if match:
            days, hours, minutes, seconds = map(int, match.groups())
            return f"{days}d {hours}h {minutes}m {seconds}s"
    except:
        pass
    return "unknown time"

def get_nfl_data():
    """Fetch NFL player data"""
    params = {
        'key': API_KEY
    }
    
    try:
        response = requests.get(API_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            error_data = response.json()
            if "message" in error_data:
                if "Quota" in error_data["message"]:
                    time_remaining = parse_quota_message(error_data["message"])
                    st.error(f"API quota exceeded. Quota will reset in: {time_remaining}")
                else:
                    st.error(error_data["message"])
            else:
                st.error("Access denied. Please check your API key.")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
        
        return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None

def process_nfl_data(data):
    """Process NFL data into DataFrame"""
    if not data:
        return pd.DataFrame()
    
    try:
        df = pd.DataFrame(data)
        
        # Rename columns for better display
        column_mapping = {
            'TeamID': 'Team ID',
            'Team': 'Team',
            'Number': 'Jersey Number',
            'FirstName': 'First Name',
            'LastName': 'Last Name',
            'Position': 'Position',
            'Status': 'Status',
            'Height': 'Height',
            'Weight': 'Weight',
            'BirthDate': 'Birth Date',
            'College': 'College',
            'Experience': 'Experience',
            'PhotoUrl': 'Photo URL'
        }
        
        # Rename only existing columns
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Convert birth dates
        if 'Birth Date' in df.columns:
            df['Birth Date'] = pd.to_datetime(df['Birth Date']).dt.date
            df['Age'] = (pd.Timestamp.now().date() - df['Birth Date']).astype('<m8[Y]')
        
        # Format height and weight
        if 'Height' in df.columns:
            df['Height'] = df['Height'].apply(lambda x: f"{x // 12}'{x % 12}\"" if pd.notnull(x) else 'Unknown')
        if 'Weight' in df.columns:
            df['Weight'] = df['Weight'].apply(lambda x: f"{int(x)} lbs" if pd.notnull(x) else 'Unknown')
        
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
    tab1, tab2 = st.tabs(["NFL Players", "Zodiac Calculator"])
    
    with tab1:
        # Add refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
            
        # Fetch NFL data
        with st.spinner("Loading NFL player data..."):
            data = get_nfl_data()
            
            if data:
                df = process_nfl_data(data)
                
                if not df.empty:
                    # Create layout
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.subheader("Filters")
                        
                        # Search box
                        search = st.text_input("Search players", placeholder="Name, team, or college...")
                        
                        # Dynamic filters
                        filter_columns = ['Team', 'Position', 'Status', 'College']
                        filters = {}
                        
                        for col in filter_columns:
                            if col in df.columns:
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
                        st.write(f"Showing {len(filtered_df)} players")
                        st.dataframe(filtered_df)
                        
                        # Export functionality
                        if st.button("Export to CSV"):
                            csv = filtered_df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"nfl_players_{datetime.now().strftime('%Y%m%d')}.csv",
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
