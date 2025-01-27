import pandas as pd
import streamlit as st

# Example DataFrame to demonstrate functionality
# Replace this with actual data or a dynamic loading mechanism
data = {
    "Player Name": ["Tom Brady", "Peyton Manning", "Joe Montana", "Aaron Rodgers"],
    "Jersey Number": [12, 18, 16, 22],
    "Compatible Zodiacs": ["Aquarius", "", "Gemini", "Leo"],
}
df = pd.DataFrame(data)

# Function to apply custom highlighting rules
def highlight_rows(row):
    """
    Highlight cells for compatible zodiacs in yellow and
    repeated jersey numbers in green.
    """
    # Create a list of styles for each cell in the row
    styles = [""] * len(row)
    
    # Highlight Compatible Zodiacs in yellow
    if row["Compatible Zodiacs"] != "":
        styles[row.index.get_loc("Compatible Zodiacs")] = "background-color: yellow"
    
    # Highlight repeated jersey numbers in green
    try:
        jersey_number = int(row["Jersey Number"])
        if jersey_number % 11 == 0:  # Check if the number has repeated digits like 22, 33, etc.
            styles[row.index.get_loc("Jersey Number")] = "background-color: green"
    except ValueError:
        # Skip styling if Jersey Number is not an integer
        pass
    
    return styles

# Main function to run the Streamlit app
def main():
    # Streamlit app title
    st.title("NFL Player Data with Highlights")
    st.write("This table highlights compatible zodiacs and repeated jersey numbers.")

    # Display original DataFrame
    st.subheader("Original Data")
    st.dataframe(df, use_container_width=True)

    # Apply styling to the DataFrame
    styled_df = df.style.apply(highlight_rows, axis=1)

    # Display the styled DataFrame
    st.subheader("Highlighted Data")
    st.dataframe(styled_df, use_container_width=True)

# Run the Streamlit app
if __name__ == "__main__":
    main()
