import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Countdown Stats", layout="wide")
st.title("🎵 Live Song Countdown Dashboard")

# The URL you provided (Public CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQJhiV_Pa-naVPS--8plhf4I7Qh0HdH4mOVl4D2bql-fe87W5SN1wxwB52Bo1d_Q4yd1eC6RdXPiBez/pub?output=csv"

# Function to load data
@st.cache_data(ttl=600) # Refresh data every 10 minutes
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()

    # --- TOP METRICS ---
    total_votes = len(df)
    unique_voters = df['gigyaUserId'].nunique()
    top_song = df['Song'].mode()[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Votes", f"{total_votes:,}")
    m2.metric("Unique Voters", f"{unique_voters:,}")
    m3.metric("Current #1", top_song)

    st.divider()

    # --- CHARTS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Songs")
        top_songs = df['Song'].value_counts().head(10).reset_index()
        top_songs.columns = ['Song', 'Votes']
        fig_songs = px.bar(top_songs, x='Votes', y='Song', orientation='h', 
                           color='Votes', color_continuous_scale='Viridis')
        fig_songs.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_songs, use_container_width=True)

    with col2:
        st.subheader("Top 10 Artists")
        top_artists = df['Artist'].value_counts().head(10).reset_index()
        top_artists.columns = ['Artist', 'Votes']
        fig_artists = px.bar(top_artists, x='Votes', y='Artist', orientation='h',
                             color='Votes', color_continuous_scale='Magma')
        fig_artists.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_artists, use_container_width=True)

    # --- VOTING SOURCE ---
    st.subheader("How people are voting")
    source_counts = df['Source'].value_counts().reset_index()
    fig_pie = px.pie(source_counts, values='count', names='Source', hole=0.4)
    st.plotly_chart(fig_pie)

    # --- DATA TABLE ---
    with st.expander("See Raw Records"):
        st.write(df)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure your Google Sheet is still published to the web as a CSV.")
