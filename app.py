import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import re

# API Configuration
API_KEY = "6df769b0923f4826a1fbb8080e55cdf4"
API_URL = "https://api.sportsdata.io/v3/nfl/scores/json/PlayersByAvailable"

def parse_quota_message(response):
    """Extract time remaining from quota message"""
    try:
        # Try to get error details from response
        if hasattr(response, 'json'):
            error_data = response.json()
            message = error_data.get('message', '')
            
            # Check for various time formats in the message
            # Try dd:hh:mm:ss format
            time_match = re.search(r"(\d+):(\d+):(\d+):(\d+)", message)
            if time_match:
                days, hours, mins, secs = map(int, time_match.groups())
                return f"{days}d {hours}h {mins}m {secs}s"
            
            # Try "in X hours" format
            hours_match = re.search(r"in (\d+) hours?", message)
            if hours_match:
                hours = int(hours_match.group(1))
                return f"{hours} hours"
            
            # Try "in X minutes" format
            mins_match = re.search(r"in (\d+) minutes?", message)
            if mins_match:
                mins = int(mins_match.group(1))
                return f"{mins} minutes"
                
            # If we have a message but couldn't parse time
            if message:
                return message
    except:
        pass
    return "Please try again later"

[Rest of the code remains exactly the same...]
