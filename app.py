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
            (120, 'Capricorn'),
            (219, 'Aquarius'),
            (320, 'Pisces'),
            (420, 'Aries'),
            (521, 'Taurus'),
            (621, 'Gemini'),
            (723, 'Cancer'),
            (823, 'Leo'),
            (923, 'Virgo'),
            (1023, 'Libra'),
            (1122, 'Scorpio'),
            (1222, 'Sagittarius'),
            (1232, 'Capricorn')
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
    
    result_df = pd.DataFrame()
    for api_col, display_col in columns.items():
        if api_col in df.columns:
            result_df[display_col] = df[api_col]
        else:
            result_df[display_col] = None
    
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

def highlight_rows(row, compatible_signs, repeated_numbers):
    """Highlight compatible zodiacs in yellow and repeated numbers in green"""
    styles = []
    if row['Zodiac'] in compatible_signs:
        styles.append('background-color: yellow')
    if row['Number'] in repeated_numbers:
        styles.append('background-color: green')
    return '; '.join(styles)

def main():
    st.title("NFL Players Roster: Zodiac Edition")

    st.sidebar.header("Zodiac Calculator")
    default_date = date(1988, 1, 1)
    user_date = st.sidebar.date_input(
        "Enter your birth date (MM/DD/YYYY)",
        value=default_date,
        format="MM/DD/YYYY"
    )
    
    user_zodiac = get_zodiac_sign(user_date)
    st.sidebar.write(f"Your Zodiac Sign: **{user_zodiac}**")
    
    compatible_signs = get_compatible_signs(user_zodiac)
    st.sidebar.write("Most Compatible Signs:")
    for sign in compatible_signs:
        st.sidebar.write(f"- {sign}")

    show_compatible = st.sidebar.checkbox("Show only compatible players", value=False)

    st.sidebar.divider()
    st.sidebar.header("Filters")

    with st.spinner("Loading players..."):
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to fetch data from the API")
        st.stop()

    df = process_player_data(data)

    unique_teams = df['Team'].unique()
    unique_positions = df['Position'].unique()
    valid_teams = sorted([team for team in unique_teams if team])
    valid_positions = sorted([pos for pos in unique_positions if pos])

    selected_team = st.sidebar.selectbox(
        "Select Team",
        ["All Teams"] + valid_teams
    )

    selected_position = st.sidebar.selectbox(
        "Select Position",
        ["All Positions"] + valid_positions
    )

    filtered_df = df

    if show_compatible:
        filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]

    if selected_team != "All Teams":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]

    if selected_position != "All Positions":
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]

    search = st.text_input("Search players", "")

    if search:
        search_lower = search.lower()
        mask = (
            filtered_df['First Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Last Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Team'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['College'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = filtered_df[mask]

    if show_compatible:
        st.write(f"Showing {len(filtered_df)} compatible players")
    else:
        st.write(f"Showing {len(filtered_df)} players")

    repeated_numbers = filtered_df['Number'][filtered_df['Number'].duplicated(keep=False)]

    styled_df = filtered_df.style.apply(
        lambda x: highlight_rows(x, compatible_signs, repeated_numbers), axis=1
    )

    st.dataframe(styled_df, use_container_width=True)

    if st.button("Export to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"nfl_players_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
