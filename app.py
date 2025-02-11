Yes, that's the complete code to handle the HTML roster data with all the required functionality. It includes:

```python
import streamlit as st
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def process_roster_data(file_content):
    position_map = {
        'LWR': 'WR', 'RWR': 'WR', 'SWR': 'WR',
        'LDE': 'DE', 'RDE': 'DE',
        'WLB': 'LB', 'MLB': 'LB', 'ROLB': 'LB',
        'LCB': 'CB', 'RCB': 'CB',
        'PK': 'Kicker'
    }
    exclude_positions = {'PT', 'LS', 'H', 'KO', 'PR', 'KR', 'FUT'}
    
    soup = BeautifulSoup(file_content, 'html.parser')
    data = []
    current_team = None
    
    for row in soup.find_all('tr'):
        if row.find('td', class_='dt-sh-all'):
            current_team = row.find('td').text.split('-')[1].strip()
            continue
            
        cells = row.find_all('td')
        if len(cells) >= 4 and current_team:
            team = cells[0].text.strip()
            pos = cells[1].text.strip()
            
            if pos in exclude_positions:
                continue
                
            pos = position_map.get(pos, pos)
            number = cells[2].text.strip()
            name = cells[3].find('a').text.strip() if cells[3].find('a') else ''
            
            if name:
                data.append({
                    'Team': team,
                    'Position': pos,
                    'Number': number,
                    'Name': name
                })
    
    return pd.DataFrame(data)

def main():
    st.set_page_config(page_title="NFL Roster Explorer", page_icon="🏈", layout="wide")
    st.title("🏈 NFL Roster Explorer")
    
    uploaded_file = st.file_uploader("Upload NFL Roster File", type=['txt', 'html'])
    
    if uploaded_file:
        file_content = uploaded_file.getvalue().decode('utf-8')
        df = process_roster_data(file_content)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Filters")
            search = st.text_input("Search players", placeholder="Name or number...")
            
            filter_columns = ['Team', 'Position']
            filters = {}
            for col in filter_columns:
                values = ['All'] + sorted(df[col].unique().tolist())
                filters[col] = st.selectbox(f'Filter by {col}', values)
        
        with col2:
            filtered_df = df.copy()
            
            for col, value in filters.items():
                if value != 'All':
                    filtered_df = filtered_df[filtered_df[col] == value]
            
            if search:
                search_lower = search.lower()
                mask = filtered_df.astype(str).apply(
                    lambda x: x.str.lower().str.contains(search_lower, na=False)
                ).any(axis=1)
                filtered_df = filtered_df[mask]
            
            st.write(f"Showing {len(filtered_df)} players")
            st.dataframe(filtered_df)
            
            if st.button("Export to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"nfl_roster_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
```

Remember to install beautifulsoup4: `pip install beautifulsoup4`
