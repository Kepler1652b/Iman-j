from datetime import datetime


# Function to convert Unix timestamp to readable format
def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts