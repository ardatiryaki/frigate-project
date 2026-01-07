import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuration
DB_FILE = "tracker.db"
POLL_INTERVAL = 5

st.set_page_config(page_title="Frigate Activity Tracker", page_icon="📊", layout="wide")

def get_data(date_str):
    """Fetch logs for a specific date."""
    conn = sqlite3.connect(DB_FILE)
    query = f"SELECT * FROM activity_logs WHERE timestamp LIKE '{date_str}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    st.title("📊 Frigate Activity Dashboard")
    
    # Sidebar: Date Selection
    st.sidebar.header("Settings")
    selected_date = st.sidebar.date_input("Select Date", datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Fetch Data
    df = get_data(date_str)
    
    if df.empty:
        st.warning(f"No data found for {date_str}")
        return

    # Process Data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Summary Metrics
    status_counts = df['state'].value_counts()
    
    total_logs = len(df)
    total_seconds = total_logs * POLL_INTERVAL
    
    # Calculate durations
    work_sec = status_counts.get('WORKING', 0) * POLL_INTERVAL
    rest_sec = status_counts.get('RESTING', 0) * POLL_INTERVAL
    away_sec = status_counts.get('AWAY', 0) * POLL_INTERVAL
    
    # Formatting helper
    def format_time(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m"

    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric("💻 Work Time", format_time(work_sec), delta="Working")
    col2.metric("🛌 Rest Time", format_time(rest_sec), delta="Resting")
    col3.metric("🚪 Away Time", format_time(away_sec), delta="Away")
    
    st.divider()

    # Charts Row
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Daily Distribution")
        # Prepare data for Pie Chart
        stats_df = pd.DataFrame({
            'State': ['WORKING', 'RESTING', 'AWAY'],
            'Seconds': [work_sec, rest_sec, away_sec]
        })
        # Filter out zero values
        stats_df = stats_df[stats_df['Seconds'] > 0]
        
        fig = px.pie(stats_df, values='Seconds', names='State', 
                     color='State',
                     color_discrete_map={'WORKING':'#FFA500', 'RESTING':'#4169E1', 'AWAY':'#808080'},
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Timeline Activity")
        # Timeline logic: Resample to 5-minute buckets using 'max' or 'mode' logic?
        # Simpler: Histogram of timestamp by state
        
        fig_hist = px.histogram(df, x="timestamp", color="state", 
                                color_discrete_map={'WORKING':'#FFA500', 'RESTING':'#4169E1', 'AWAY':'#808080'},
                                nbins=100,
                                title="Activity Over Time")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Raw Data Expander
    with st.expander("View Raw Data"):
        st.dataframe(df.sort_values(by='timestamp', ascending=False))

if __name__ == "__main__":
    main()
