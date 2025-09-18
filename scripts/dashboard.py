import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ----------------- PAGE CONFIG -----------------
st.set_page_config(layout="wide", page_title="Pollution Source Dashboard")
st.title("🌍 Pollution Source Dashboard")

# ----------------- LOAD DATA -----------------
df = pd.read_csv("data/labeled_data.csv")

# ----------------- SIDEBAR FILTERS -----------------
# Pollution Sources
sources = df["pollution_source"].unique().tolist()
selected_sources = st.sidebar.multiselect(
    "Select Pollution Sources",
    options=sources,
    default=sources,
    key="pollution_sources"
)

# ----------------- FILTER DATA -----------------
df_filtered_sources = df[df["pollution_source"].isin(selected_sources)]
st.write(f"Displaying {df_filtered_sources.shape[0]} locations for Pollution Sources Map")

# ----------------- POLLUTION SOURCES MAP -----------------
m_sources = folium.Map(
    location=[df_filtered_sources["latitude"].mean(), df_filtered_sources["longitude"].mean()],
    zoom_start=4
)

# Source colors
source_colors = {
    "Vehicular": "red",
    "Industrial": "green",
    "Agricultural": "orange",
    "Burning": "purple",
    "Natural": "blue"
}

# Add all filtered points
for _, row in df_filtered_sources.iterrows():
    folium.Circle(
        location=[row["latitude"], row["longitude"]],
        radius=2000,
        color=source_colors.get(row["pollution_source"], "gray"),
        fill=True,
        fill_opacity=0.6,
        popup=f"Location: {row['location_id']}<br>Source: {row['pollution_source']}"
    ).add_to(m_sources)

# Add legend for sources
legend_html_sources = """
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 150px; height: 140px; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white;">
&emsp;<b>Pollution Sources</b><br>
&emsp;<i style="color:red;">●</i> Vehicular<br>
&emsp;<i style="color:green;">●</i> Industrial<br>
&emsp;<i style="color:orange;">●</i> Agricultural<br>
&emsp;<i style="color:purple;">●</i> Burning<br>
&emsp;<i style="color:blue;">●</i> Natural
</div>
"""
m_sources.get_root().html.add_child(folium.Element(legend_html_sources))

st.subheader("Pollution Sources Map")
st_folium(m_sources, width=1200, height=700)

from folium.plugins import MarkerCluster

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ----------------- PAGE CONFIG -----------------
st.set_page_config(layout="wide", page_title="Pollution Dashboard")
st.title("🌍 Pollution Dashboard by Pollutant")

# ----------------- LOAD DATA -----------------
df = pd.read_csv("data/labeled_data.csv")

# Drop rows with missing lat/lon
df = df.dropna(subset=["latitude", "longitude"])

# ----------------- SIDEBAR -----------------
# List of pollutants
pollutants = ["pm2_5","pm10","no2","so2","o3","co","aqi","temperature","humidity","wind_speed","temp_humidity_index","pollution_wind_ratio"]
selected_pollutant = st.sidebar.selectbox("Select Pollutant to Visualize", pollutants)

# ----------------- CREATE MAP -----------------
m_pollutant = folium.Map(
    location=[df["latitude"].mean(), df["longitude"].mean()],
    zoom_start=4
)

# Marker cluster
marker_cluster = MarkerCluster().add_to(m_pollutant)

# Normalize pollutant values for color intensity
min_val = df[selected_pollutant].min()
max_val = df[selected_pollutant].max()
range_val = max_val - min_val if max_val - min_val != 0 else 1

# Function to map pollutant to color
def pollutant_color(val):
    # Green → Yellow → Red
    norm = (val - min_val) / range_val
    if norm < 0.33:
        return "green"
    elif norm < 0.66:
        return "orange"
    else:
        return "red"

# Add markers
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=pollutant_color(row[selected_pollutant]),
        fill=True,
        fill_opacity=0.7,
        popup=f"Location: {row['location_id']}<br>{selected_pollutant}: {row[selected_pollutant]:.2f}"
    ).add_to(marker_cluster)

st.subheader(f"🗺️ {selected_pollutant} Map")
st_folium(m_pollutant, width=1200, height=700)
