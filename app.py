import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# Configuration
API_KEY = "6df769b0923f4826a1fbb8080e55cdf4"
API_URL = "https://api.sportsdata.io/v3/nfl/scores/json/PlayersByAvailable"

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
            (1231, 'Capricorn')  # Dec 22 - Dec 31
        ]

        birth_day_of_year = month * 100 + day

        for cutoff, sign in zodiac_dates:
            if birth_day_of_year <= cutoff:
                return sign
        return 'Capricorn'
    except Exception as e:
        return 'Unknown'

def fetch_nfl_players():
    """Fetch NFL players using the API"""
    try:
        headers = {"Ocp-Apim-Subscription-Key": API_KEY}
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch data from the API.")
            return []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

def main():
    st.title("NFL Players Zodiac Sign and Jersey Analysis")

    # Fetch NFL players
    data = fetch_nfl_players()
    if not data:
        st.stop()

    # Process data
    df = pd.DataFrame(data)
    if df.empty:
        st.error("No data available to display.")
        return

    df = df[['Name', 'BirthDate', 'Jersey', 'Position', 'Team']]
    df['BirthDate'] = pd.to_datetime(df['BirthDate'], errors='coerce')
    df['Zodiac'] = df['BirthDate'].apply(get_zodiac_sign)

    # Zodiac Compatibility (for demonstration purposes, simplified logic)
    zodiac_compatibility = {
        'Aries': ['Leo', 'Sagittarius'],
        'Taurus': ['Virgo', 'Capricorn'],
        'Gemini': ['Libra', 'Aquarius'],
        'Cancer': ['Scorpio', 'Pisces'],
        'Leo': ['Aries', 'Sagittarius'],
        'Virgo': ['Taurus', 'Capricorn'],
        'Libra': ['Gemini', 'Aquarius'],
        'Scorpio': ['Cancer', 'Pisces'],
        'Sagittarius': ['Aries', 'Leo'],
        'Capricorn': ['Taurus', 'Virgo'],
        'Aquarius': ['Gemini', 'Libra'],
        'Pisces': ['Cancer', 'Scorpio']
    }

    def compatible_zodiacs(zodiac):
        return ', '.join(zodiac_compatibility.get(zodiac, []))

    df['Compatible Zodiacs'] = df['Zodiac'].apply(compatible_zodiacs)

    # Highlighting Function
    def highlight_cells(val, col):
        if col == 'Compatible Zodiacs' and val != '':
            return 'background-color: yellow'
        elif col == 'Jersey' and isinstance(val, (int, float)) and int(val) % 11 == 0:
            return 'background-color: green'
        return ''

    styled_df = df.style.applymap(lambda val: highlight_cells(val, 'Compatible Zodiacs'), subset=['Compatible Zodiacs'])
    styled_df = styled_df.applymap(lambda val: highlight_cells(val, 'Jersey'), subset=['Jersey'])

    st.write("### NFL Players Data")
    st.dataframe(styled_df, use_container_width=True)

if __name__ == "__main__":
    main()
