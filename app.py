import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# [Previous code remains the same until the main() function]

def is_repeating_number(num):
    """Check if a number is repeating (e.g., 22, 33, 44)"""
    if pd.isna(num) or not isinstance(num, (int, float)):
        return False
    num_str = str(int(num))
    return len(num_str) > 1 and len(set(num_str)) == 1

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

    # Add search functionality
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

    # Create style conditions for the dataframe
    def style_dataframe(df):
        styles = []
        
        # Style for compatible zodiac signs (yellow background)
        styles.append(
            df.style.apply(lambda x: ['background-color: #ffeb3b' if zodiac in compatible_signs else '' 
                                    for zodiac in x], subset=['Zodiac'])
        )
        
        # Style for repeating numbers (green background)
        styles.append(
            df.style.apply(lambda x: ['background-color: #4caf50' if is_repeating_number(num) else '' 
                                    for num in x], subset=['Number'])
        )
        
        return df.style.apply(lambda x: [''] * len(x))  # Base style

    # Display styled dataframe
    st.dataframe(
        style_dataframe(filtered_df),
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
