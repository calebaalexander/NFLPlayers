import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuration
API_KEY = "6df769b0923f4826a1fbb8080e55cdf4"
API_URL = "https://api.sportsdata.io/v3/nfl/scores/json/PlayersByAvailable"

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
    
    # Print raw data for debugging
    if st.checkbox("Show raw data sample"):
        st.write("Sample of raw data:", df.head())
    
    # Select and rename columns
    columns = {
        'Team': 'Team',
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
        result_df['Birth Date'] = pd.to_datetime(result_df['Birth Date']).dt.strftime('%Y-%m-%d')
        result_df['Age'] = df['BirthDate'].apply(calculate_age)
    
    # Fill any NA values in Team column
    result_df['Team'] = result_df['Team'].fillna('Free Agent')
    
    return result_df

def main():
    st.title("NFL Players Roster")

    # Create sidebar for filters
    st.sidebar.header("Filters")

    # Fetch data
    with st.spinner("Loading players..."):
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to fetch data from the API")
        st.stop()

    # Process data
    df = process_player_data(data)
    
    # Get unique teams and handle None values
    unique_teams = df['Team'].unique()
    valid_teams = sorted([team for team in unique_teams if team])
    
    # Team filter in sidebar
    selected_team = st.sidebar.selectbox(
        "Select Team",
        ["All Teams"] + valid_teams
    )

    # Filter based on team selection
    filtered_df = df
    if selected_team != "All Teams":
        filtered_df = df[df['Team'] == selected_team]

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
