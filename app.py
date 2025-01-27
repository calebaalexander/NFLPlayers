import streamlit as st
import pandas as pd
from datetime import datetime

# Function to calculate zodiac sign
def get_zodiac_sign(birth_date):
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
        (1222, 'Sagittarius') # Nov 22 - Dec 21
    ]
    zodiac_dates = sorted(zodiac_dates, key=lambda x: x[0])

    day_of_year = int(birth_date.strftime("%j"))
    for cutoff, sign in zodiac_dates:
        if day_of_year <= cutoff:
            return sign
    return 'Capricorn'

# Sample data loading (Replace this with your real data loading logic)
data = {
    "Team": ["ARI", "IND", "Free Agent", "Free Agent"],
    "Position": ["K", "QB", "QB", "K"],
    "Number": [5, 15, 5, 9],
    "First Name": ["Matt", "Joe", "Matt", "Robbie"],
    "Last Name": ["Prater", "Flacco", "Ryan", "Gould"],
    "Height": ["5'10", "6'6", "6'4", "6'0"],
    "Weight": ["201 lbs", "230 lbs", "220 lbs", "190 lbs"],
    "Birth Date": ["1984-08-10", "1985-01-16", "1985-05-17", "1982-12-06"],
    "Zodiac": ["Leo", "Capricorn", "Taurus", "Sagittarius"],
    "College": ["Central FL", "Delaware", "Boston Coll.", "Penn State"]
}

df = pd.DataFrame(data)

# User input for Zodiac compatibility
birth_date_input = st.text_input("Enter your birth date (MM/DD/YYYY)", "01/01/1988")
if birth_date_input:
    user_zodiac = get_zodiac_sign(birth_date_input)
    st.write(f"Your Zodiac Sign: {user_zodiac}")
    compatible_signs = ["Taurus", "Virgo", "Pisces"]
    st.write(f"Most Compatible Signs: {', '.join(compatible_signs)}")

# Highlight function for Zodiac compatibility and repeated numbers
def highlight_cells(row):
    zodiac_color = ""
    number_color = ""
    if row["Zodiac"] in compatible_signs:
        zodiac_color = "background-color: yellow"
    if df["Number"].duplicated(keep=False)[row.name]:  # Check for duplicates
        number_color = "background-color: green"
    
    return [
        "",  # Team
        "",  # Position
        number_color,  # Number
        "",  # First Name
        "",  # Last Name
        "",  # Height
        "",  # Weight
        "",  # Birth Date
        zodiac_color,  # Zodiac
        "",  # College
    ]

# Apply styling to the DataFrame
styled_df = df.style.apply(highlight_cells, axis=1)

# Display the DataFrame with styling
st.dataframe(styled_df)
