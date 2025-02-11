import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date
import base64
from io import BytesIO

# Add zodiac symbols dictionary
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

# Add zodiac traits dictionary
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

# Add NFL team colors dictionary
NFL_TEAM_COLORS = {
    'ARI': ('#97233F', '#000000'),
    'ATL': ('#A71930', '#000000'),
    'BAL': ('#241773', '#000000'),
    'BUF': ('#00338D', '#C60C30'),
    # ... Add all NFL teams
}

def format_height(height_str):
    """Convert height from inches to feet and inches format"""
    if pd.isna(height_str):
        return None
    try:
        height_inches = int(height_str)
        feet = height_inches // 12
        inches = height_inches % 12
        return f"{feet}' {inches}\""
    except:
        return height_str

def is_angel_number(number):
    """Check if a number is an angel number (all digits the same)"""
    if pd.isna(number):
        return False
    number_str = str(int(number))
    return len(number_str) > 1 and len(set(number_str)) == 1

def format_date(date_obj):
    """Format date as YYYY/MM/DD"""
    if pd.isna(date_obj):
        return None
    try:
        return pd.to_datetime(date_obj).strftime('%Y/%m/%d')
    except:
        return date_obj

def get_position_zodiac_distribution(df):
    """Calculate most common zodiac sign for each position"""
    return df.groupby('Position')['Zodiac'].agg(lambda x: x.value_counts().index[0]).reset_index()

def main():
    st.title("NFL Players Roster: Zodiac Edition")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Player Roster", "Position Zodiac Analysis"])
    
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
    user_number = st.sidebar.number_input("Enter your Lucky Number", min_value=0, max_value=99, value=7)
    
    # Load and process data
    df = load_nfl_data(2024)  # Load current year data
    
    # Process zodiac information
    user_zodiac = get_zodiac_sign(user_date)
    compatible_signs = get_compatible_signs(user_zodiac)
    
    # Display user's zodiac info
    st.sidebar.write(f"Your Zodiac Sign: {ZODIAC_SYMBOLS[user_zodiac]} **{user_zodiac}**")
    st.sidebar.write(f"Traits: {ZODIAC_TRAITS[user_zodiac]}")
    
    # Show compatible signs with symbols
    st.sidebar.write("Most Compatible Signs:")
    for sign in compatible_signs:
        st.sidebar.write(f"{ZODIAC_SYMBOLS[sign]} {sign}")
    
    # Compatible players toggle (default checked)
    show_compatible = st.sidebar.checkbox("Show only compatible players", value=True)
    
    # Angel numbers toggle
    show_angel = st.sidebar.checkbox("Show only Angel numbers", value=False)
    
    with tab1:
        # Birthday matches section
        st.subheader("Birthday Matches")
        user_birthday = user_date.strftime('%m-%d')
        birthday_matches = df[df['Birth Date'].dt.strftime('%m-%d') == user_birthday]
        
        if not birthday_matches.empty:
            for _, player in birthday_matches.iterrows():
                exact_match = player['Birth Date'].date() == user_date
                player_text = f"{player['First Name']} {player['Last Name']} ({format_date(player['Birth Date'])})"
                if exact_match:
                    st.markdown(f"**:gold[{player_text}]**")
                else:
                    st.write(player_text)
                    
                # Check for lucky number match
                if player['Number'] == user_number:
                    st.write(f"🎯 Matching lucky number: {user_number}!")
        else:
            st.write("No players share your birthday.")
        
        # Main roster display
        st.subheader("Player Roster")
        
        # Apply filters
        filtered_df = df.copy()
        
        if show_compatible:
            filtered_df = filtered_df[filtered_df['Zodiac'].isin(compatible_signs)]
            
        if show_angel:
            filtered_df = filtered_df[filtered_df['Number'].apply(is_angel_number)]
        
        # Display the enhanced dataframe
        st.dataframe(
            filtered_df,
            column_config={
                "Team": st.column_config.Column(
                    "Team",
                    help="NFL Team",
                    width="medium",
                ),
                "Zodiac": st.column_config.Column(
                    "Zodiac",
                    help=lambda x: ZODIAC_TRAITS.get(x, ""),
                ),
                "Number": st.column_config.NumberColumn(
                    "Number",
                    format="%d",
                ),
                "Height": st.column_config.TextColumn(
                    "Height",
                    width="small",
                ),
                "Birth Date": st.column_config.TextColumn(
                    "Birth Date",
                    width="medium",
                )
            }
        )
    
    with tab2:
        st.subheader("Position Zodiac Analysis")
        zodiac_dist = get_position_zodiac_distribution(df)
        
        # Create visualization of position-zodiac distribution
        for _, row in zodiac_dist.iterrows():
            st.write(f"{row['Position']}: {ZODIAC_SYMBOLS[row['Zodiac']]} {row['Zodiac']}")

if __name__ == "__main__":
    main()
