import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date

# Constants
ZODIAC_SYMBOLS = {
    'Aries': '♈',
    'Taurus': '♉',
    'Gemini': '♊',
    'Cancer': '♋',
    'Leo': '♌',
    'Virgo': '♍',
    'Libra': '♎',
    'Scorpio': '♏',
    'Sagittarius': '♐',
    'Capricorn': '♑',
    'Aquarius': '♒',
    'Pisces': '♓'
}

ZODIAC_TRAITS = {
    'Aries': 'Confident, competitive, natural leader',
    'Taurus': 'Reliable, patient, determined',
    'Gemini': 'Adaptable, versatile, quick learner',
    'Cancer': 'Protective, intuitive, team-oriented',
    'Leo': 'Charismatic, confident, born leader',
    'Virgo': 'Detail-oriented, analytical, hardworking',
    'Libra': 'Balanced, diplomatic, fair',
    'Scorpio': 'Intense, strategic, powerful',
    'Sagittarius': 'Optimistic, adventurous, independent',
    'Capricorn': 'Disciplined, responsible, manager',
    'Aquarius': 'Innovative, progressive, original',
    'Pisces': 'Intuitive, empathetic, adaptable'
}

# Helper functions
def format_height(height_str):
    """Convert height from inches to feet and inches format"""
    if pd.isna(height_str):
        return None
    try:
        height_inches = int(float(height_str))
        feet = height_inches // 12
        inches = height_inches % 12
        return f"{feet}' {inches}\""
    except:
        return str(height_str)

def format_date(date_obj):
    """Format date as YYYY/MM/DD"""
    if pd.isna(date_obj):
        return None
    try:
        return pd.to_datetime(date_obj).strftime('%Y/%m/%d')
    except:
        return str(date_obj)

def is_angel_number(number):
    """Check if a number is an angel number (all digits the same)"""
    if pd.isna(number):
        return False
    try:
        number_str = str(int(number))
        return len(number_str) > 1 and len(set(number_str)) == 1
    except:
        return False

# Zodiac-related functions
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

def get_position_zodiac_distribution(df):
    """Calculate most common zodiac sign for each position"""
    try:
        return df.groupby('Position')['Zodiac'].agg(
            lambda x: x.value_counts().index[0] if len(x) > 0 else None
        ).reset_index()
    except:
        return pd.DataFrame(columns=['Position', 'Zodiac'])

# Data loading and processing
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_nfl_data(year):
    """Load NFL roster data for a given year"""
    try:
        df = pd.DataFrame()
        try:
            # Try regular roster import first as it's faster
            df = nfl.import_rosters([year])
            if df is None or df.empty:
                # Fallback to weekly rosters if needed
                df = nfl.import_weekly_rosters([year])
                if df is not None and not df.empty:
                    df = df.sort_values('week', ascending=False).groupby('player_id').first().reset_index()
        except Exception as e:
            st.error(f"Could not retrieve roster data: {str(e)}")
            return None
        
        if df is None or df.empty:
            st.error(f"No data available for year {year}")
            return None
            
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def process_dataframe(df):
    """Process the dataframe to ensure consistent column names and formats"""
    try:
        # Create a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Remove unnecessary columns
        columns_to_drop = ['player_id', 'status', 'full_name', 'entry_year', 'rookie_year', 'depth_chart_position']
        processed_df = processed_df.drop(columns=columns_to_drop, errors='ignore')
        
        # Format season without comma
        if 'season' in processed_df.columns:
            processed_df['season'] = processed_df['season'].astype(str).str.replace(',', '')
        
        # Standardize column names
        column_mappings = {
            'jersey_number': 'Number',
            'position': 'Position',
            'team': 'Team',
            'height': 'Height',
            'weight': 'Weight',
            'birth_date': 'Birth Date',
            'player_name': 'Name',
            'season': 'Season'
        }
        
        # Rename columns that exist in the dataframe
        processed_df = processed_df.rename(columns={k: v for k, v in column_mappings.items() if k in processed_df.columns})
        
        # Process only necessary columns
        if 'birth_date' in processed_df.columns:
            processed_df['Birth Date'] = pd.to_datetime(processed_df['birth_date'])
        elif 'Birth Date' in processed_df.columns:
            processed_df['Birth Date'] = pd.to_datetime(processed_df['Birth Date'])
        
        # Process player name - ensure we're using 'Name' column
        if 'player_name' in processed_df.columns:
            processed_df['Name'] = processed_df['player_name']
        elif 'full_name' in processed_df.columns:
            processed_df['Name'] = processed_df['full_name']
        
        # Format height
        if 'height' in processed_df.columns:
            processed_df['Height'] = processed_df['height'].apply(format_height)
        elif 'Height' in processed_df.columns:
            processed_df['Height'] = processed_df['Height'].apply(format_height)
        
        # Ensure Number column is numeric
        if 'Number' in processed_df.columns:
            processed_df['Number'] = pd.to_numeric(processed_df['Number'], errors='coerce')
        
        # Add Zodiac column
        processed_df['Zodiac'] = processed_df['Birth Date'].apply(get_zodiac_sign)
        
        # Format dates for display
        processed_df['Birth Date'] = processed_df['Birth Date'].apply(format_date)
        
        return processed_df
    
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None
# Load and process data
    with st.spinner('Loading NFL player data... (this may take a few moments on first load)'):
        raw_df = load_nfl_data(selected_year)
        if raw_df is None:
            st.error("Could not load NFL data. Please try a different year.")
            st.stop()
            
        df = process_dataframe(raw_df)
        if df is None:
            st.error("Could not process NFL data.")
            st.stop()
def main():
    st.title("NFL Players Roster: Zodiac Edition")
    
    # Sidebar inputs
    st.sidebar.header("Zodiac Calculator")
    
    # Birthday input
    default_date = date(1988, 10, 25)
    user_date = st.sidebar.date_input(
        "Enter your birth date (YYYY/MM/DD)",
        value=default_date,
        format="YYYY/MM/DD"
    )
    
    # Lucky number input
    user_number = st.sidebar.number_input(
        "Enter your Lucky Number",
        min_value=0,
        max_value=99,
        value=13
    )
    
    # Year selection
    selected_year = st.sidebar.selectbox(
        "Select Year",
        range(2024, 2012, -1),
        index=0
    )
    
    # Load and process data
    with st.spinner("Loading NFL player data..."):
        raw_df = load_nfl_data(selected_year)
        if raw_df is None:
            st.error("Could not load NFL data. Please try a different year.")
            st.stop()
            
        df = process_dataframe(raw_df)
        if df is None:
            st.error("Could not process NFL data.")
            st.stop()
    
    # Calculate user's zodiac info
    user_zodiac = get_zodiac_sign(user_date)
    compatible_signs = get_compatible_signs(user_zodiac)
    
    # Display user's zodiac info
    st.sidebar.write(f"Your Zodiac Sign: {ZODIAC_SYMBOLS.get(user_zodiac, '')} **{user_zodiac}**")
    st.sidebar.write(f"Traits: {ZODIAC_TRAITS.get(user_zodiac, '')}")
    
    # Show compatible signs with symbols
    st.sidebar.write("Most Compatible Signs:")
    for sign in compatible_signs:
        st.sidebar.write(f"{ZODIAC_SYMBOLS.get(sign, '')} {sign}")

    # Sidebar filters
    st.sidebar.divider()
    st.sidebar.header("Filters")
    
    # Team filter in sidebar
    unique_teams = sorted(df['Team'].dropna().unique())
    selected_team = st.sidebar.selectbox(
        "Select Team",
        ["All Teams"] + list(unique_teams)
    )

    # Position filter in sidebar
    unique_positions = sorted(df['Position'].dropna().unique())
    selected_position = st.sidebar.selectbox(
        "Select Position",
        ["All Positions"] + list(unique_positions)
    )
    
    # Compatibility and Angel number filters in sidebar
    show_compatible = st.sidebar.checkbox("Show only compatible players", value=True)
    show_angel = st.sidebar.checkbox("Show only Angel numbers", value=False)
    
    # Search box in main area
    search = st.text_input("Search players", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply team filter
    if selected_team != "All Teams":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    # Apply position filter
    if selected_position != "All Positions":
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]
    
    # Apply compatibility filter
    if show_compatible:
        filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]
    
    # Apply angel numbers filter
    if show_angel:
        filtered_df = filtered_df[filtered_df['Number'].apply(is_angel_number)]
    
    if search:
        search_lower = search.lower()
        mask = (
            filtered_df['First Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Last Name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Team'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['Position'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = filtered_df[mask]
    
   # Tabs for different views
    tab1, tab2 = st.tabs(["Player Roster", "Position Zodiac Analysis"])
    
    with tab1:
        # Display roster first
        st.subheader("Player Roster")
        # Select and reorder columns for display
        display_columns = ['Name', 'Season', 'Team', 'Position', 'Number', 'Birth Date', 'Height', 'Zodiac']
        display_df = filtered_df[display_columns]
        
        st.dataframe(
            display_df,
            hide_index=True,  # Hide the index column
            column_config={
                "Zodiac": st.column_config.Column(
                    "Zodiac",
                    help="Hover for zodiac traits"
                ),
                "Number": st.column_config.NumberColumn(
                    "Number",
                    format="%d"
                ),
                "Birth Date": st.column_config.TextColumn(
                    "Birth Date"
                ),
                "Height": st.column_config.TextColumn(
                    "Height"
                ),
                "Season": st.column_config.NumberColumn(
                    "Season",
                    format="%d"
                )
            }
        )
        
        # Birthday matches section below
        st.subheader("Birthday Matches")
        user_birthday = user_date.strftime('%m-%d')
        
        # Convert Birth Date back to datetime for comparison
        birthday_matches = df[pd.to_datetime(df['Birth Date']).dt.strftime('%m-%d') == user_birthday]
        
        if not birthday_matches.empty:
            birthday_matches = birthday_matches.sort_values('Birth Date', ascending=False)
            for _, player in birthday_matches.iterrows():
                exact_match = pd.to_datetime(player['Birth Date']).date() == user_date
                player_text = f"{player['Name']} ({player['Birth Date']})"
                
                if exact_match:
                    st.markdown(f"**:gold[{player_text}]**")
                else:
                    st.write(player_text)
                
                if pd.notna(player['Number']) and int(player['Number']) == user_number:
                    st.write(f"🎯 Matching lucky number: {user_number}!")
        else:
            st.write("No players share your birthday.")
    
    with tab2:
        st.subheader("Position Zodiac Analysis")
        zodiac_dist = get_position_zodiac_distribution(df)
        
        for _, row in zodiac_dist.iterrows():
            if row['Zodiac']:
                st.write(f"{row['Position']}: {ZODIAC_SYMBOLS.get(row['Zodiac'], '')} {row['Zodiac']}")
