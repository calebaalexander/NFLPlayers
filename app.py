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
        # Add zodiac sign right after birth date
        result_df['Zodiac'] = result_df['Birth Date'].apply(get_zodiac_sign)
        # Format birth date for display
        result_df['Birth Date'] = result_df['Birth Date'].dt.strftime('%Y-%m-%d')
    
    # Fill any NA values
    result_df['Team'] = result_df['Team'].fillna('Free Agent')
    result_df['Position'] = result_df['Position'].fillna('Unknown')
    
    # Reorder columns to ensure Zodiac comes right after Birth Date
    cols = result_df.columns.tolist()
    birth_date_idx = cols.index('Birth Date')
    cols.remove('Zodiac')
    cols.insert(birth_date_idx + 1, 'Zodiac')
    result_df = result_df[cols]
    
    return result_df

def main():
    st.title("NFL Players Roster: Zodiac Edition")

    # Create sidebar for filters
    st.sidebar.header("Zodiac Calculator")
    
    # Add date input for zodiac calculation with default date of Jan 1, 1988
    default_date = date(1988, 1, 1)
    user_date = st.sidebar.date_input(
        "Enter your birth date (MM/DD/YYYY)",
        value=default_date,
        format="MM/DD/YYYY"
    )
    
    # Calculate and display user's zodiac sign
    user_zodiac = get_zodiac_sign(user_date)
    st.sidebar.write(f"Your Zodiac Sign: **{user_zodiac}**")
    
    # Display compatible signs
    compatible_signs = get_compatible_signs(user_zodiac)
    st.sidebar.write("Most Compatible Signs:")
    for sign in compatible_signs:
        st.sidebar.write(f"- {sign}")
        
    # Add toggle for compatibility filter
    show_compatible = st.sidebar.checkbox("Show only compatible players", value=False)

    st.sidebar.divider()
    st.sidebar.header("Filters")

    # Fetch data
    with st.spinner("Loading players..."):
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to fetch data from the API")
        st.stop()

    # Process data
    df = process_player_data(data)
    
    # Get unique teams and positions
    unique_teams = df['Team'].unique()
    unique_positions = df['Position'].unique()
    valid_teams = sorted([team for team in unique_teams if team])
    valid_positions = sorted([pos for pos in unique_positions if pos])
    
    # Team filter in sidebar
    selected_team = st.sidebar.selectbox(
        "Select Team",
        ["All Teams"] + valid_teams
    )
    
    # Position filter in sidebar
    selected_position = st.sidebar.selectbox(
        "Select Position",
        ["All Positions"] + valid_positions
    )

    # Filter based on selections
    filtered_df = df

    # Apply zodiac compatibility filter
    if show_compatible:
        filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]

    # Apply team filter
    if selected_team != "All Teams":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    # Apply position filter
    if selected_position != "All Positions":
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]

    # Add search functionality in main area
    search = st.text_input("Search players", "")
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        mask = (
            filtered_df['First Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Last Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Team'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['College'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = filtered_df[mask]

    # Display metrics
    if show_compatible:
        st.write(f"Showing {len(filtered_df)} compatible players")
    else:
        st.write(f"Showing {len(filtered_df)} players")

    # Display table
    st.dataframe(
        filtered_df,
        hide_index=True,
        column_config={
            "Number": st.column_config.NumberColumn(
                "Number",
                format="%d"
            ),
            "Weight": st.column_config.NumberColumn(
                "Weight",
                format="%d lbs"
            ),
            "Age": st.column_config.NumberColumn(
                "Age",
                format="%d"
            )
        }
    )

    # Export functionality
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
