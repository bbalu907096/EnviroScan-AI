import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/keerthi.thatikonda/Desktop/EnviroScan/data/labeled_data.csv")  # adjust path if needed
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

pollution_sources = df["pollution_source"].dropna().unique().tolist()
selected_sources = st.sidebar.multiselect("Select Pollution Sources", pollution_sources, default=pollution_sources)

months = sorted(df["month"].dropna().unique())
selected_months = st.sidebar.multiselect("Select Month(s)", months, default=months)

seasons = df["season"].dropna().unique().tolist()
selected_seasons = st.sidebar.multiselect("Select Season(s)", seasons, default=seasons)

remove_missing = st.sidebar.checkbox("Remove missing coordinates", value=True)

# -----------------------------
# Filter Data
# -----------------------------
filtered_df = df[
    (df["pollution_source"].isin(selected_sources)) &
    (df["month"].isin(selected_months)) &
    (df["season"].isin(selected_seasons))
]

if remove_missing:
    filtered_df = filtered_df.dropna(subset=["latitude", "longitude"])

st.write(f"Displaying {filtered_df.shape[0]} locations for selected filters")

# -----------------------------
# Map
# -----------------------------
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    m = folium.Map(
        location=[filtered_df["latitude"].mean(), filtered_df["longitude"].mean()],
        zoom_start=6
    )

    marker_cluster = MarkerCluster().add_to(m)

    source_colors = {
        "Vehicular": "red",
        "Industrial": "green",
        "Agricultural": "orange",
        "Burning": "purple",
        "Natural": "blue"
    }

    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            color=source_colors.get(row["pollution_source"], "gray"),
            fill=True,
            fill_opacity=0.7,
            popup=f"Location: {row['location_id']}<br>Source: {row['pollution_source']}"
        ).add_to(marker_cluster)

    st.subheader("🗺️ Pollution Sources Map")
    st_folium(m, width=1200, height=700)

# -----------------------------
# Charts
# -----------------------------
if not filtered_df.empty:
    st.subheader("📊 Pollution Source Distribution")
    fig1 = px.histogram(
        filtered_df,
        x="pollution_source",
        title="Pollution Source Frequency",
        color="pollution_source"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📈 AQI Distribution by Source")
    fig2 = px.box(
        filtered_df,
        x="pollution_source",
        y="aqi",
        title="AQI Distribution by Pollution Source",
        color="pollution_source"
    )
    st.plotly_chart(fig2, use_container_width=True)
