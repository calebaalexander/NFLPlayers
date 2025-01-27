import streamlit as st
import pandas as pd
import requests
import plotly.express as px
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

def process_player_data(data):
    """Convert API data to pandas DataFrame with relevant columns"""
    df = pd.DataFrame(data)
    # Select relevant columns
    columns = ['Name', 'Team', 'Position', 'Age', 'Experience', 'Height', 'Weight', 
              'College', 'Status', 'PhotoUrl']
    df = df[columns].copy()
    return df

def main():
    st.title("NFL Players Dashboard")
    st.sidebar.header("Filters")

    # Fetch data
    data = fetch_nfl_data()
    if not data:
        st.stop()

    # Process data
    df = process_player_data(data)

    # Sidebar filters
    selected_teams = st.sidebar.multiselect(
        "Select Teams",
        options=sorted(df['Team'].unique()),
        default=[]
    )

    selected_positions = st.sidebar.multiselect(
        "Select Positions",
        options=sorted(df['Position'].unique()),
        default=[]
    )

    # Filter data based on selections
    filtered_df = df.copy()
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Team'].isin(selected_teams)]
    if selected_positions:
        filtered_df = filtered_df[filtered_df['Position'].isin(selected_positions)]

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", len(filtered_df))
    with col2:
        st.metric("Average Age", round(filtered_df['Age'].mean(), 1))
    with col3:
        st.metric("Average Experience", round(filtered_df['Experience'].mean(), 1))

    # Create visualizations
    st.subheader("Position Distribution")
    position_count = filtered_df['Position'].value_counts()
    fig_position = px.pie(values=position_count.values, 
                         names=position_count.index, 
                         title="Players by Position")
    st.plotly_chart(fig_position)

    st.subheader("Age Distribution by Position")
    fig_age = px.box(filtered_df, 
                     x="Position", 
                     y="Age",
                     title="Age Distribution by Position")
    st.plotly_chart(fig_age)

    # Display player table
    st.subheader("Player List")
    st.dataframe(filtered_df.sort_values('Name'))

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
