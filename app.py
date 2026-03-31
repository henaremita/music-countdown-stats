import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Ultimate Countdown Dashboard", page_icon="🎧", layout="wide")

# Optional: Add a little custom CSS for a cleaner look
st.markdown("""
<style>
    .stMetric {
        background-color: #f3f4f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQJhiV_Pa-naVPS--8plhf4I7Qh0HdH4mOVl4D2bql-fe87W5SN1wxwB52Bo1d_Q4yd1eC6RdXPiBez/pub?output=csv"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Convert 'Date Entered' to actual datetime objects for time charting
    df['Date Entered'] = pd.to_datetime(df['Date Entered'], format='mixed', utc=True).dt.tz_localize(None)
    return df

try:
    raw_df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3252/3252813.png", width=80) # Generic music icon
    st.sidebar.title("🎛️ Filters")
    
    # Artist Filter
    all_artists = sorted(raw_df['Artist'].dropna().unique())
    selected_artists = st.sidebar.multiselect("Select Artists:", all_artists, placeholder="All Artists")
    
    # Source Filter
    all_sources = raw_df['Source'].unique()
    selected_sources = st.sidebar.multiselect("Select Source:", all_sources, placeholder="All Sources")

    # Apply Filters
    df = raw_df.copy()
    if selected_artists:
        df = df[df['Artist'].isin(selected_artists)]
    if selected_sources:
        df = df[df['Source'].isin(selected_sources)]

    # --- MAIN DASHBOARD HEADER ---
    st.title("🎧 Ultimate Song Countdown Dashboard")
    st.markdown("Live statistics and voting trends, updated automatically.")
    st.divider()

    # --- KPI METRICS ---
    if not df.empty:
        total_votes = len(df)
        unique_voters = df['gigyaUserId'].nunique()
        avg_votes = total_votes / unique_voters if unique_voters > 0 else 0
        top_song = df['Song'].mode()[0] if not df.empty else "N/A"
        top_artist = df['Artist'].mode()[0] if not df.empty else "N/A"

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Votes", f"{total_votes:,}")
        m2.metric("Unique Voters", f"{unique_voters:,}")
        m3.metric("Avg Votes/Person", f"{avg_votes:.1f}")
        m4.metric("Current #1 Song", top_song)
        m5.metric("Top Artist", top_artist)
        st.write("") # Spacing

        # --- ORGANIZE WITH TABS ---
        tab1, tab2, tab3 = st.tabs(["🏆 Leaderboards", "📈 Voting Trends", "🗂️ Data Deep Dive"])

        with tab1:
            st.subheader("The Top 10s")
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Songs Bar Chart
                top_songs = df['Song'].value_counts().head(10).reset_index()
                top_songs.columns = ['Song', 'Votes']
                fig_songs = px.bar(top_songs, x='Votes', y='Song', orientation='h', 
                                   color='Votes', color_continuous_scale='Sunset', text='Votes')
                fig_songs.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                fig_songs.update_traces(textposition='outside')
                st.plotly_chart(fig_songs, use_container_width=True)

            with col2:
                # Top Artists Bar Chart
                top_artists = df['Artist'].value_counts().head(10).reset_index()
                top_artists.columns = ['Artist', 'Votes']
                fig_artists = px.bar(top_artists, x='Votes', y='Artist', orientation='h',
                                     color='Votes', color_continuous_scale='Tealgrn', text='Votes')
                fig_artists.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                fig_artists.update_traces(textposition='outside')
                st.plotly_chart(fig_artists, use_container_width=True)

        with tab2:
            st.subheader("Voting Momentum Over Time")
            # Group votes by day
            daily_votes = df.groupby(df['Date Entered'].dt.date).size().reset_index(name='Votes')
            daily_votes.columns = ['Date', 'Votes']
            
            fig_timeline = px.area(daily_votes, x='Date', y='Votes', markers=True, 
                                   color_discrete_sequence=['#8338ec'])
            st.plotly_chart(fig_timeline, use_container_width=True)

        with tab3:
            col_tree, col_pie = st.columns([2, 1])
            
            with col_tree:
                st.subheader("Artist & Song Breakdown")
                st.caption("Click on an Artist to see their specific songs.")
                # Treemap of Artist -> Song (Only for top 50 to avoid clutter)
                top_50_artists = df['Artist'].value_counts().head(50).index
                tree_df = df[df['Artist'].isin(top_50_artists)]
                fig_tree = px.treemap(tree_df, path=[px.Constant("All Votes"), 'Artist', 'Song'], 
                                      color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_tree.update_traces(root_color="lightgrey")
                st.plotly_chart(fig_tree, use_container_width=True)
                
            with col_pie:
                st.subheader("Voting Method")
                source_counts = df['Source'].value_counts().reset_index()
                fig_pie = px.pie(source_counts, values='count', names='Source', hole=0.5,
                                 color_discrete_sequence=['#ff006e', '#3a86ff'])
                st.plotly_chart(fig_pie, use_container_width=True)

        # --- RAW DATA EXPANDER ---
        with st.expander("🔍 View & Download Raw Filtered Data"):
            st.dataframe(df.sort_values(by="Date Entered", ascending=False), use_container_width=True)
            
    else:
        st.warning("No data matches your current filters. Try removing them in the sidebar.")

except Exception as e:
    st.error("Error loading the dashboard. Please check your Google Sheet connection.")
    st.exception(e)
