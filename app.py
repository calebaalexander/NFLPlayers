import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date

# [Previous constant definitions for ZODIAC_SYMBOLS and ZODIAC_TRAITS remain the same...]

@st.cache_data
def load_nfl_data(year):
    """Load NFL roster data for a given year"""
    try:
        df = pd.DataFrame()
        
        try:
            df = nfl.import_weekly_rosters([year])
            if df is not None and not df.empty:
                df = df.sort_values('week', ascending=False).groupby('player_id').first().reset_index()
        except:
            try:
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

# [Previous helper functions remain the same...]

def process_dataframe(df):
    """Process the dataframe to ensure consistent column names and formats"""
    try:
        # Create a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Standardize column names
        column_mappings = {
            'jersey_number': 'Number',
            'position': 'Position',
            'team': 'Team',
            'height': 'Height',
            'weight': 'Weight',
            'birth_date': 'Birth Date'
        }
        
        # Rename columns that exist in the dataframe
        processed_df = processed_df.rename(columns={k: v for k, v in column_mappings.items() if k in processed_df.columns})
        
        # Process birth date
        if 'birth_date' in processed_df.columns:
            processed_df['Birth Date'] = pd.to_datetime(processed_df['birth_date'])
        
        # Process player name
        if 'player_name' in processed_df.columns:
            processed_df[['First Name', 'Last Name']] = processed_df['player_name'].str.split(' ', n=1, expand=True)
        elif 'full_name' in processed_df.columns:
            processed_df[['First Name', 'Last Name']] = processed_df['full_name'].str.split(' ', n=1, expand=True)
        
        # Format height
        if 'Height' in processed_df.columns:
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
    
    # Lucky number input (starting with 13)
    user_number = st.sidebar.number_input(
        "Enter your Lucky Number",
        min_value=0,
        max_value=99,
        value=13  # Changed to 13
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
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Player Roster", "Position Zodiac Analysis"])
    
    with tab1:
        # Birthday matches section
        st.subheader("Birthday Matches")
        user_birthday = user_date.strftime('%m-%d')
        
        # Convert Birth Date back to datetime for comparison
        df['Birth Date'] = pd.to_datetime(df['Birth Date'])
        birthday_matches = df[df['Birth Date'].dt.strftime('%m-%d') == user_birthday]
        
        if not birthday_matches.empty:
            birthday_matches = birthday_matches.sort_values('Birth Date', ascending=False)
            for _, player in birthday_matches.iterrows():
                exact_match = player['Birth Date'].date() == user_date
                player_text = f"{player['First Name']} {player['Last Name']} ({format_date(player['Birth Date'])})"
                
                if exact_match:
                    st.markdown(f"**:gold[{player_text}]**")
                else:
                    st.write(player_text)
                
                if 'Number' in player and pd.notna(player['Number']) and int(player['Number']) == user_number:
                    st.write(f"🎯 Matching lucky number: {user_number}!")
        else:
            st.write("No players share your birthday.")
        
        # Convert Birth Date back to string for display
        df['Birth Date'] = df['Birth Date'].apply(format_date)
        
        # Filters
        show_compatible = st.sidebar.checkbox("Show only compatible players", value=True)
        show_angel = st.sidebar.checkbox("Show only Angel numbers", value=False)
        
        # Filter data
        filtered_df = df.copy()
        if show_compatible:
            filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]
        if show_angel:
            filtered_df = filtered_df[filtered_df['Number'].apply(is_angel_number)]
        
        # Display roster
        st.subheader("Player Roster")
        st.dataframe(
            filtered_df,
            column_config={
                "Zodiac": st.column_config.Column(
                    "Zodiac",
                    help="Hover for zodiac traits",
                    width="medium"
                ),
                "Number": st.column_config.NumberColumn(
                    "Number",
                    format="%d"
                ),
                "Birth Date": st.column_config.TextColumn(
                    "Birth Date",
                    width="medium"
                )
            }
        )
    
    with tab2:
        st.subheader("Position Zodiac Analysis")
        zodiac_dist = get_position_zodiac_distribution(df)
        
        for _, row in zodiac_dist.iterrows():
            if row['Zodiac']:
                st.write(f"{row['Position']}: {ZODIAC_SYMBOLS.get(row['Zodiac'], '')} {row['Zodiac']}")

if __name__ == "__main__":
    main()
