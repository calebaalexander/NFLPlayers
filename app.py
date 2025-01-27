import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Configuration
API_KEY = "bd4ea5c3d5e54628bd67f2862a210e5b"
BASE_URL = "https://api.sportsdata.io/v3/nfl"

# Zodiac Sign Mapping
ZODIAC_SIGNS = {
    (1, 20): 'Capricorn', (2, 19): 'Aquarius', (3, 21): 'Pisces', 
    (4, 20): 'Aries', (5, 21): 'Taurus', (6, 21): 'Gemini', 
    (7, 23): 'Cancer', (8, 23): 'Leo', (9, 23): 'Virgo', 
    (10, 23): 'Libra', (11, 22): 'Scorpio', (12, 22): 'Sagittarius'
}

# Most Compatible Signs
MOST_COMPATIBLE = ['Pisces', 'Taurus', 'Cancer']

def get_zodiac_sign(birth_date):
    """Determine zodiac sign based on birth date"""
    if not birth_date:
        return None
    try:
        date = datetime.strptime(birth_date, "%Y-%m-%d")
        month, day = date.month, date.day
        
        for (start_month, start_day), sign in sorted(ZODIAC_SIGNS.items(), reverse=True):
            if (month, day) >= (start_month, start_day):
                return sign
        return ZODIAC_SIGNS[(12, 22)]  # Capricorn for dates before Jan 20
    except (ValueError, TypeError):
        return None

def is_angel_number(number):
    """Check if a number is an angel number (repeating digits)"""
    if not number:
        return False
    str_num = str(number)
    return len(str_num) > 1 and len(set(str_num)) == 1

def check_social_info():
    # Test with a few well-known players
    player_ids = [
        "18055",  # Patrick Mahomes
        "21683",  # Justin Herbert
        "19001"   # Josh Allen
    ]
    
    st.subheader("NFL Player Social Media and Zodiac Analysis")
    
    # Create a list to store player data
    player_data = []
    
    for player_id in player_ids:
        url = f"{BASE_URL}/scores/json/Player/{player_id}?key={API_KEY}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                player_info = {
                    'PlayerID': player_id,
                    'Name': data.get('Name', 'N/A'),
                    'BirthDate': data.get('BirthDate', 'N/A'),
                    'BirthCity': data.get('BirthCity', 'N/A'),
                    'BirthState': data.get('BirthState', 'N/A'),
                    'College': data.get('College', 'N/A'),
                    'PhotoUrl': data.get('PhotoUrl', 'N/A')
                }
                
                # Determine Zodiac Sign
                zodiac_sign = get_zodiac_sign(data.get('BirthDate'))
                player_info['ZodiacSign'] = zodiac_sign
                
                # Detect Angel Numbers in various numeric fields
                angel_numbers = []
                numeric_fields = [
                    ('PlayerID', player_id),
                    ('Height', data.get('Height')),
                    ('Weight', data.get('Weight'))
                ]
                
                for field_name, field_value in numeric_fields:
                    if is_angel_number(field_value):
                        angel_numbers.append(f"{field_name}: {field_value}")
                
                player_info['AngelNumbers'] = ', '.join(angel_numbers) if angel_numbers else 'None'
                
                player_data.append(player_info)
                
                # Display individual player information
                st.write(f"### {player_info['Name']}")
                st.write(f"- Birth Date: {player_info['BirthDate']}")
                st.write(f"- Zodiac Sign: {zodiac_sign}")
                st.write(f"- Angel Numbers: {player_info['AngelNumbers']}")
                st.divider()
            else:
                st.error(f"Error {response.status_code} for player {player_id}")
        except Exception as e:
            st.error(f"Error checking player {player_id}: {str(e)}")
    
    # Create DataFrame for comprehensive view
    if player_data:
        df = pd.DataFrame(player_data)
        
        # Highlight Most Compatible Zodiac Signs
        def highlight_zodiac(val):
            return 'background-color: yellow' if val in MOST_COMPATIBLE else ''
        
        # Highlight Angel Numbers
        def highlight_angel_numbers(val):
            return 'background-color: lightgreen' if val != 'None' else ''
        
        # Apply conditional formatting
        styled_df = df.style.applymap(highlight_zodiac, subset=['ZodiacSign']) \
                            .applymap(highlight_angel_numbers, subset=['AngelNumbers'])
        
        st.subheader("Player Data Overview")
        st.dataframe(styled_df)

def main():
    st.title("NFL Player Social Media and Zodiac Analysis")
    
    with st.spinner("Analyzing player information..."):
        check_social_info()

if __name__ == "__main__":
    main()
