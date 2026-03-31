import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Config
st.set_page_config(page_title="Countdown Live Stats", layout="wide")
st.title("🎵 Live Song Countdown Dashboard")

# 1. Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Read Data (Use your Sheet URL here)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQJhiV_Pa-naVPS--8plhf4I7Qh0HdH4mOVl4D2bql-fe87W5SN1wxwB52Bo1d_Q4yd1eC6RdXPiBez/pub?output=csv"
df = conn.read(spreadsheet=url, ttl="10m") # Updates every 10 mins

# 3. Top Level Metrics
total_votes = len(df)
unique_voters = df['gigyaUserId'].nunique()
top_song = df['Song'].mode()[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Votes", total_votes)
col2.metric("Unique Voters", unique_voters)
col3.metric("Current #1 Song", top_song)

# 4. Charts
st.divider()
left_co, right_co = st.columns(2)

with left_co:
    st.subheader("Top 10 Songs")
    song_counts = df['Song'].value_counts().head(10)
    st.bar_chart(song_counts, color="#FF4B4B")

with right_co:
    st.subheader("Top 10 Artists")
    artist_counts = df['Artist'].value_counts().head(10)
    st.bar_chart(artist_counts, color="#1DE9B6")

# 5. Raw Data Table (Optional)
with st.expander("View Raw Voting Data"):
    st.dataframe(df)
