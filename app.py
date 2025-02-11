import streamlit as st
import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date

# Add these imports at the top
import numpy as np 
import plotly.express as px

# ... (existing code remains the same until main() function)

def main():
    st.title("NFL Players Roster: Zodiac Edition")
    
    # Create sidebar for filters 
    st.sidebar.header("Zodiac Calculator")
    
    # Add date input and lucky number for zodiac calculation
    col1, col2 = st.sidebar.columns(2)
    with col1:
        default_date = date(1988, 10, 25)
        user_date = st.date_input(
            "Enter your birth date",
            value=default_date,
            format="YYYY-MM-DD" 
        )
    with col2:    
        lucky_number = st.number_input("Enter your lucky number", min_value=0, max_value=99, value=7)
    
    # Calculate and display user's zodiac sign
    user_zodiac = get_zodiac_sign(user_date)
    st.sidebar.write(f"Your Zodiac Sign: **{user_zodiac}**")
    
    # Display compatible signs
    compatible_signs = get_compatible_signs(user_zodiac)
    st.sidebar.write("Most Compatible Signs:")
    for sign in compatible_signs:
        st.sidebar.write(f"- {sign}")
    
    # Add toggle for compatibility filter (default to checked) 
    show_compatible = st.sidebar.checkbox("Show only compatible players", value=True)

    st.sidebar.divider()
    st.sidebar.header("Filters")

    # Year selection
    selected_year = st.sidebar.selectbox(
        "Select Year", 
        range(2024, 2012, -1),
        index=0  
    )

    # ... (data loading code remains the same)
        
    # Get unique teams and positions  
    unique_teams = sorted(df['Team'].dropna().unique())
    unique_positions = sorted(df['Position'].dropna().unique())
    
    # Add team logos and colors
    team_info = {
        'ARI': {'logo': 'ari.png', 'colors': ['#97233F', '#FFB612']},
        'ATL': {'logo': 'atl.png', 'colors': ['#A71930', '#000000']},
        # ... add info for all teams
    }
    
    df['TeamLogo'] = df['Team'].map(lambda x: team_info[x]['logo'] if x in team_info else '')
    df['TeamColor'] = df['Team'].map(lambda x: team_info[x]['colors'][0] if x in team_info else 'gray')

    # Add zodiac symbols and descriptions 
    zodiac_info = {
        'Aries': {'symbol': '♈', 'description': 'Energetic, enthusiastic, impulsive'},  
        'Taurus': {'symbol': '♉', 'description': 'Reliable, stubborn, enjoys luxury'}, 
        # ... add all zodiac signs
    }

    df['ZodiacSymbol'] = df['Zodiac'].map(lambda x: zodiac_info[x]['symbol'] if x in zodiac_info else '')
    df['ZodiacDescription'] = df['Zodiac'].map(lambda x: zodiac_info[x]['description'] if x in zodiac_info else '')

    # Format height 
    df['Height'] = df['Height'].apply(lambda x: f"{x[0]}' {x[1]}\"" if isinstance(x, list) and len(x) == 2 else x)

    # ... (filtering code remains mostly the same)

    # Zodiac MVP - players with same birthday as user
    birthday_df = df[df['Birth Date'].dt.strftime('%m-%d') == user_date.strftime('%m-%d')]
    birthday_df['BirthYearDiff'] = birthday_df['Birth Date'].dt.year - user_date.year
    birthday_df['Matching'] = birthday_df.apply(lambda x: 'Birthday Match' if x['BirthYearDiff'] == 0 else '', axis=1)

    if not birthday_df.empty:
        st.subheader("Players sharing your birthday")
        styled_birthday_df = birthday_df.style\
            .applymap(lambda x: 'background-color: gold; font-weight: bold' if x == 'Birthday Match' else '',
                     subset=['Matching'])\
            .format({"Birth Date": lambda t: t.strftime("%Y/%m/%d")})
        
        st.dataframe(styled_birthday_df[['First Name', 'Last Name', 'Team', 'Number', 'Birth Date', 'Matching']],
                     hide_index=True)

    # Lucky number match  
    lucky_number_df = birthday_df[birthday_df['Number'] == lucky_number]
    if not lucky_number_df.empty:
        st.subheader("WOW! These players share your birthday AND lucky number! 🎉")
        st.dataframe(lucky_number_df[['First Name', 'Last Name', 'Team', 'Number', 'Birth Date']], hide_index=True)

    # ... (original dataframe display code remains mostly the same)

    # Add tabs
    tab1, tab2 = st.tabs(["Player Table", "Zodiac Analysis"])
    
    # Move the original dataframe display into first tab
    with tab1:
        styled_df = filtered_df.style\
            .applymap(lambda x: 'background-color: yellow' if x in compatible_signs else '', 
                     subset=['Zodiac'])\
            .applymap(lambda x: 'background-color: green' 
                     if pd.notnull(x) and isinstance(x, (int, float)) and 
                     len(str(int(x))) > 1 and len(set(str(int(x)))) == 1 
                     else '', subset=['Number'])

        st.dataframe(
            styled_df.format({"Birth Date": lambda t: t.strftime("%Y/%m/%d")}),
            hide_index=True,
            column_config={
                # ... (column config remains the same)
            }
        )

    # Add zodiac analysis in second tab  
    with tab2:
        st.subheader("Zodiac Sign Distribution by Position")

        position_zodiac_df = pd.crosstab(df['Position'], df['Zodiac'])
        position_zodiac_df = position_zodiac_df.reindex(index=unique_positions, columns=list(zodiac_info.keys()))
        position_zodiac_df = position_zodiac_df.fillna(0).astype(int) 

        # Find the most common zodiac sign for each position
        max_zodiac = position_zodiac_df.idxmax(axis=1)

        fig = px.imshow(position_zodiac_df,
                        labels=dict(x="Zodiac Sign", y="Position", color="Player Count"),
                        x=list(zodiac_info.keys()), 
                        y=unique_positions,
                        color_continuous_scale='Viridis',
                        text_auto=True)

        fig.update_layout(title_text='Zodiac Sign Distribution by Position', title_x=0.5)  

        st.plotly_chart(fig)

        st.subheader("Most Common Zodiac Sign by Position")
        for position, zodiac in max_zodiac.items():
            st.write(f"- {position}: {zodiac} {zodiac_info[zodiac]['symbol']}")

if __name__ == "__main__":
    main()
