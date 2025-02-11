import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date

@st.cache_data
def load_nfl_data(year):
    """Load NFL roster data for a given year"""
    try:
        # Request roster data with specific columns
        df = pd.DataFrame() # Initialize empty DataFrame
        
        try:
            # Try to get seasonal roster data
            df = nfl.import_weekly_rosters([year])
            if df is not None and not df.empty:
                # If we have weekly data, take the most recent week for each player
                df = df.sort_values('week', ascending=False).groupby('player_id').first().reset_index()
        except:
            try:
                # Fallback to plain roster import
                df = nfl.import_rosters([year])
            except:
                st.error("Could not retrieve roster data")
                return None
        
        if df is None or df.empty:
            st.error(f"No data available for year {year}")
            return None
            
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
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
    """Calculate age from birth date"""
    if pd.isna(birth_date):
        return None
    try:
        birth_date = pd.to_datetime(birth_date)
        today = pd.Timestamp.now()
        return int((today - birth_date).days / 365.25)
    except:
        return None

def main():
    st.title("NFL Players Roster: Zodiac Edition")
    
    # Create sidebar for filters
    st.sidebar.header("Zodiac Calculator")
    
    # Add date input for zodiac calculation
    default_date = date(1988, 10, 25)  # Changed to October 25, 1988
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

    # Year selection - set to max 2024
    selected_year = st.sidebar.selectbox(
        "Select Year",
        range(2024, 2012, -1),  # From 2024 down to 2012
        index=0
    )

    # Load data with progress indicator
    with st.spinner("Loading NFL player data..."):
        df = load_nfl_data(selected_year)
        
        if df is None:
            st.error("Could not load NFL data. Please try a different year.")
            st.stop()
        
        # Process the data
        df['Birth Date'] = pd.to_datetime(df['birth_date'])
        df['Age'] = df['Birth Date'].apply(calculate_age)
        df['Zodiac'] = df['Birth Date'].apply(get_zodiac_sign)
        
        # Split player name into first and last name if player_name exists
        if 'player_name' in df.columns:
            df[['First Name', 'Last Name']] = df['player_name'].str.split(' ', n=1, expand=True)
        elif 'full_name' in df.columns:
            df[['First Name', 'Last Name']] = df['full_name'].str.split(' ', n=1, expand=True)
        else:
            # Create from first and last name if they exist separately
            df['First Name'] = df.get('first_name', '')
            df['Last Name'] = df.get('last_name', '')
        
        # Rename columns (handling possible variations in column names)
        column_mappings = {
            'team': 'Team',
            'position': 'Position',
            'jersey_number': 'Number',
            'height': 'Height',
            'weight': 'Weight',
            'college': 'College'
        }
        
        df = df.rename(columns={k: v for k, v in column_mappings.items() if k in df.columns})
        
        # Round numeric columns to whole numbers
        numeric_columns = ['Weight', 'Number', 'Age']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)
        
        # Select and reorder columns, only including those that exist
        desired_columns = ['First Name', 'Last Name', 'Team', 'Position', 'Number', 
                         'Birth Date', 'Zodiac', 'Age', 'Height', 'Weight', 'College']
        actual_columns = [col for col in desired_columns if col in df.columns]
        df = df[actual_columns]

    # Get unique teams and positions (handling possible None/NaN values)
    unique_teams = sorted(df['Team'].dropna().unique())
    unique_positions = sorted(df['Position'].dropna().unique())
    
    # Team filter in sidebar
    selected_team = st.sidebar.selectbox(
        "Select Team",
        ["All Teams"] + list(unique_teams)
    )
    
    # Position filter in sidebar
    selected_position = st.sidebar.selectbox(
        "Select Position",
        ["All Positions"] + list(unique_positions)
    )

    # Filter data
    filtered_df = df.copy()

    if show_compatible:
        filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]

    if selected_team != "All Teams":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    if selected_position != "All Positions":
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]

    # Search functionality
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

    # Display metrics
    st.write(f"Showing {len(filtered_df)} players")

    # Style the dataframe
    styled_df = filtered_df.style\
        .applymap(lambda x: 'background-color: yellow' if x in compatible_signs else '', 
                 subset=['Zodiac'])\
        .applymap(lambda x: 'background-color: green' 
                 if pd.notnull(x) and isinstance(x, (int, float)) and 
                 len(str(int(x))) > 1 and len(set(str(int(x)))) == 1 
                 else '', subset=['Number'])

    # Display the dataframe with integer formats
    st.dataframe(
        styled_df,
        hide_index=True,
        column_config={
            "Number": st.column_config.NumberColumn(
                "Number",
                format="%d",
                step=1
            ),
            "Weight": st.column_config.NumberColumn(
                "Weight",
                format="%d lbs",
                step=1
            ),
            "Age": st.column_config.NumberColumn(
                "Age",
                format="%d",
                step=1
            ),
            "Birth Date": st.column_config.DateColumn(
                "Birth Date",
                format="YYYY-MM-DD"
            )
        }
    )

if __name__ == "__main__":
    main()
