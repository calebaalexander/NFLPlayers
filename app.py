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
    result_df = df[columns.keys()].copy()
    result_df.columns = columns.values()
    
    # Format birth date
    if 'Birth Date' in result_df.columns:
        result_df['Birth Date'] = pd.to_datetime(result_df['Birth Date']).dt.strftime('%Y-%m-%d')
        result_df['Age'] = df['BirthDate'].apply(calculate_age)
    
    return result_df

def main():
    st.title("NFL Players Roster")

    # Fetch data
    with st.spinner("Loading players..."):
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to fetch data from the API")
        st.stop()

    # Process and display data
    df = process_player_data(data)
    
    # Add search functionality
    search = st.text_input("Search players", "")
    
    # Filter based on search
    filtered_df = df
    if search:
        search_lower = search.lower()
        mask = (
            df['First Name'].str.lower().str.contains(search_lower, na=False) |
            df['Last Name'].str.lower().str.contains(search_lower, na=False) |
            df['Team'].str.lower().str.contains(search_lower, na=False) |
            df['College'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = df[mask]

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
