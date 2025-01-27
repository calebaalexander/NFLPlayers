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

def fetch_nfl_data():
    """Fetch NFL player data from the API"""
    params = {'key': API_KEY}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return None

def calculate_age(birth_date):
    """Calculate age from birth date, handling invalid dates"""
    try:
        birth_date = pd.to_datetime(birth_date)
        today = pd.Timestamp.now()
        age = (today - birth_date).days / 365.25
        return int(age) if pd.notnull(age) else None
    except:
        return None

def process_player_data(data):
    """Convert API data to pandas DataFrame with selected columns"""
    df = pd.DataFrame(data)
    
    # Select and rename columns
    columns = {
        'Team': 'Team',
        'Position': 'Position',
        'Number': 'Number',
        'FirstName': 'First Name',
        'LastName': 'Last Name',
        'Height': 'Height',
        'Weight': 'Weight',
        'BirthDate': 'Birth Date',
        'College': 'College'
    }
    
    # Create new dataframe with selected columns
    result_df = pd.DataFrame()
    for api_col, display_col in columns.items():
        if api_col in df.columns:
            result_df[display_col] = df[api_col]
        else:
            result_df[display_col] = None
    
    # Format birth date and calculate age
    if 'Birth Date' in result_df.columns:
        result_df['Birth Date'] = pd.to_datetime(result_df['Birth Date'])
        result_df['Age'] = result_df['Birth Date'].apply(calculate_age)
        result_df['Zodiac'] = result_df['Birth Date'].apply(get_zodiac_sign)
        result_df['Birth Date'] = result_df['Birth Date'].dt.strftime('%Y-%m-%d')
    
    result_df['Team'] = result_df['Team'].fillna('Free Agent')
    result_df['Position'] = result_df['Position'].fillna('Unknown')
    
    cols = result_df.columns.tolist()
    birth_date_idx = cols.index('Birth Date')
    cols.remove('Zodiac')
    cols.insert(birth_date_idx + 1, 'Zodiac')
    result_df = result_df[cols]
    
    return result_df

def apply_color_formatting(df, compatible_signs):
    """Apply color formatting for compatible signs and repeated numbers"""
    def highlight_compatible(row):
        return ['background-color: yellow' if row['Zodiac'] in compatible_signs else '' for _ in row]

    def highlight_repeated_numbers(column):
        return ['background-color: green' if column['Number'].duplicated(keep=False) else '' for _ in column]

    styled_df = df.style.apply(highlight_compatible, axis=1).apply(highlight_repeated_numbers)
    return styled_df

def main():
    st.title("NFL Players Roster: Zodiac Edition")

    st.sidebar.header("Zodiac Calculator")
    default_date = date(1988, 1, 1)
    user_date = st.sidebar.date_input("Enter birth date", value=default_date)
    
    user_zodiac = get_zodiac_sign(user_date)
    st.sidebar.write(f"Your Zodiac: {user_zodiac}")
    
    compatible_signs = get_compatible_signs(user_zodiac)
    st.sidebar.write("Compatible Signs:", ", ".join(compatible_signs))
    
    show_compatible = st.sidebar.checkbox("Only compatible players", value=False)
    
    with st.spinner("Loading..."):


```python
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to load data")
        st.stop()

    df = process_player_data(data)
    
    if show_compatible:
        df = df[df['Zodiac'].isin(compatible_signs)]

    styled_df = apply_color_formatting(df, compatible_signs)

    st.dataframe(styled_df, use_container_width=True)

if __name__ == "__main__":
    main()
