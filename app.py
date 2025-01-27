import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import numpy as np

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
    """Convert API data to pandas DataFrame with relevant columns"""
    df = pd.DataFrame(data)
    
    # Print available columns for debugging
    if st.checkbox("Show raw data columns"):
        st.write("Available columns:", df.columns.tolist())
    
    # Define columns mapping (API columns to display names)
    columns_mapping = {
        'PlayerID': 'Player ID',
        'TeamID': 'Team ID',
        'Team': 'Team',
        'Number': 'Number',
        'FirstName': 'First Name',
        'LastName': 'Last Name',
        'Position': 'Position',
        'Status': 'Status',
        'Height': 'Height',
        'Weight': 'Weight',
        'BirthDate': 'Birth Date',
        'College': 'College',
        'Experience': 'Experience'
    }
    
    # Select only columns that exist in the dataframe
    available_columns = [col for col in columns_mapping.keys() if col in df.columns]
    display_columns = [columns_mapping[col] for col in available_columns]
    
    # Create new dataframe with available columns
    result_df = df[available_columns].copy()
    result_df.columns = display_columns
    
    # Add full name column
    if 'First Name' in result_df.columns and 'Last Name' in result_df.columns:
        result_df['Full Name'] = result_df['First Name'] + ' ' + result_df['Last Name']
    
    # Calculate age if birth date is available
    if 'Birth Date' in result_df.columns:
        result_df['Age'] = result_df['Birth Date'].apply(calculate_age)
        # Fill NaN ages with 0 for display purposes
        result_df['Age'] = result_df['Age'].fillna(0).astype(int)
    
    # Convert experience to numeric, handling non-numeric values
    if 'Experience' in result_df.columns:
        result_df['Experience'] = pd.to_numeric(result_df['Experience'], errors='coerce')
        result_df['Experience'] = result_df['Experience'].fillna(0).astype(int)
    
    return result_df

def main():
    st.title("NFL Players Dashboard")
    st.sidebar.header("Filters")

    # Fetch data
    with st.spinner("Fetching NFL player data..."):
        data = fetch_nfl_data()
    
    if not data:
        st.error("Failed to fetch data from the API")
        st.stop()

    # Process data
    df = process_player_data(data)

    # Sidebar filters
    if 'Team' in df.columns:
        selected_teams = st.sidebar.multiselect(
            "Select Teams",
            options=sorted(df['Team'].dropna().unique()),
            default=[]
        )

    if 'Position' in df.columns:
        selected_positions = st.sidebar.multiselect(
            "Select Positions",
            options=sorted(df['Position'].dropna().unique()),
            default=[]
        )

    # Filter data based on selections
    filtered_df = df.copy()
    if selected_teams and 'Team' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Team'].isin(selected_teams)]
    if selected_positions and 'Position' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Position'].isin(selected_positions)]

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", len(filtered_df))
    with col2:
        if 'Age' in filtered_df.columns:
            avg_age = filtered_df[filtered_df['Age'] > 0]['Age'].mean()
            if pd.notnull(avg_age):
                st.metric("Average Age", round(avg_age, 1))
    with col3:
        if 'Experience' in filtered_df.columns:
            avg_exp = filtered_df['Experience'].mean()
            if pd.notnull(avg_exp):
                st.metric("Average Experience", round(avg_exp, 1))

    # Create visualizations
    if 'Position' in filtered_df.columns:
        st.subheader("Position Distribution")
        position_count = filtered_df['Position'].value_counts()
        fig_position = px.pie(values=position_count.values, 
                            names=position_count.index, 
                            title="Players by Position")
        st.plotly_chart(fig_position)

        if 'Age' in filtered_df.columns:
            st.subheader("Age Distribution by Position")
            valid_age_df = filtered_df[filtered_df['Age'] > 0]
            if not valid_age_df.empty:
                fig_age = px.box(valid_age_df, 
                               x="Position", 
                               y="Age",
                               title="Age Distribution by Position")
                st.plotly_chart(fig_age)

    # Display player table
    st.subheader("Player List")
    display_df = filtered_df.copy()
    if 'Age' in display_df.columns:
        display_df.loc[display_df['Age'] == 0, 'Age'] = None
    st.dataframe(display_df.sort_values('Full Name' if 'Full Name' in display_df.columns else display_df.columns[0]))

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
