import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date

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

@st.cache_data(show_spinner=False)
def load_nfl_data(year):
    """Load NFL roster data for a given year"""
    try:
        # Load roster data
        rosters = nfl.import_rosters([year])
        if rosters is None or len(rosters) == 0:
            return None
        return rosters
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

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

    # Year selection
    current_year = datetime.now().year
    selected_year = st.sidebar.selectbox(
        "Select Year",
        range(current_year, 2012, -1),
        index=0
    )

    # Load data
    with st.spinner("Loading NFL player data..."):
        df = load_nfl_data(selected_year)
        
        if df is None:
            st.error("Could not load NFL data. Please try again later.")
            st.stop()
        
        # Basic data processing
        df['Birth Date'] = pd.to_datetime(df['birth_date'])
        df['Age'] = df['Birth Date'].apply(calculate_age)
        df['Zodiac'] = df['Birth Date'].apply(get_zodiac_sign)
        
        # Rename columns
        df = df.rename(columns={
            'team': 'Team',
            'position': 'Position',
            'jersey_number': 'Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'height': 'Height',
            'weight': 'Weight',
            'college': 'College'
        })
        
        # Select and reorder columns
        columns = ['First Name', 'Last Name', 'Team', 'Position', 'Number', 
                  'Birth Date', 'Zodiac', 'Age', 'Height', 'Weight', 'College']
        df = df[[col for col in columns if col in df.columns]]

    # Get unique teams and positions
    unique_teams = sorted(df['Team'].unique())
    unique_positions = sorted(df['Position'].unique())
    
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

    # Display the dataframe
    st.dataframe(
        styled_df,
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
            ),
            "Birth Date": st.column_config.DateColumn(
                "Birth Date",
                format="YYYY-MM-DD"
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
