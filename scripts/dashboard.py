import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px

# ----------------- PAGE CONFIG -----------------
st.set_page_config(layout="wide", page_title="Pollution Source Dashboard")
st.title("🌍 Pollution Source Dashboard")

# ----------------- LOAD DATA -----------------
df = pd.read_csv("/Users/keerthi.thatikonda/Desktop/EnviroScan/data/labeled_data_new.csv")
df = df.dropna(subset=["latitude", "longitude", "aqi"])  # ensure no NaNs

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.header("Filters")

# Pollution Sources
sources = df["pollution_source"].unique().tolist()
selected_sources = st.sidebar.multiselect(
    "Select Pollution Sources",
    options=sources,
    default=sources,
    key="pollution_sources"
)

# Pollutants
pollutants = ["pm2_5","pm10","no2","so2","o3","co","aqi"]
selected_pollutant = st.sidebar.selectbox("Select Pollutant for Heatmap/Charts", pollutants)

# Month filter for trend chart
months = sorted(df["month"].unique())
selected_months = st.sidebar.multiselect("Select Month(s)", months, default=months)

# ----------------- FILTER DATA -----------------
df_filtered_sources = df[df["pollution_source"].isin(selected_sources)]
df_filtered_trend = df_filtered_sources[df_filtered_sources["month"].isin(selected_months)]

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
        popup=f"Location ID: {row['location_id']}<br>"
              f"Source: {row['pollution_source']}"
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

# ----------------- HEATMAP -----------------
st.subheader(f"🔥 {selected_pollutant} Heatmap")
m_heat = folium.Map(location=[df_filtered_sources["latitude"].mean(), df_filtered_sources["longitude"].mean()], zoom_start=4)
heat_data = [[row['latitude'], row['longitude'], row[selected_pollutant]] for _, row in df_filtered_sources.iterrows()]
HeatMap(heat_data, radius=15, max_zoom=13).add_to(m_heat)
st_folium(m_heat, width=1200, height=700)

# ----------------- TREND CHART -----------------
st.subheader(f"📈 {selected_pollutant} Trend by Month")
trend_df = df_filtered_trend.groupby("month")[selected_pollutant].mean().reset_index()
fig_trend = px.line(trend_df, x="month", y=selected_pollutant, markers=True, title=f"{selected_pollutant} Trend")
st.plotly_chart(fig_trend, use_container_width=True)

# ----------------- PIE CHART -----------------
st.subheader("🟢 Predicted Pollution Source Distribution")
pie_df = df_filtered_sources["pollution_source"].value_counts().reset_index()
pie_df.columns = ["pollution_source", "count"]
fig_pie = px.pie(pie_df, names="pollution_source", values="count", color="pollution_source",
                 color_discrete_map=source_colors, title="Pollution Source Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

# ----------------- ALERTS -----------------
st.subheader("⚠️ High-Risk Areas (AQI)")
aqi_threshold = 1.0  # adjust according to scaled data
high_risk = df_filtered_sources[df_filtered_sources["aqi"] > aqi_threshold]
if not high_risk.empty:
    st.warning(f"{high_risk.shape[0]} locations exceed safe AQI thresholds!")
    st.dataframe(high_risk[["location_id","locality","country","pollution_source","aqi"]])
else:
    st.success("All locations are within safe AQI levels.")

# ----------------- LOCATION (COUNTRY) FILTER & PREDICTION -----------------
st.sidebar.header("Country Filter & AQI Prediction")

# Extract country name from string if needed
df_filtered_sources["country_name"] = df_filtered_sources["country"].str.extract(r"'name':\s*'([^']+)'")

selected_country = st.sidebar.text_input("Enter Country Name")

if selected_country:
    df_country = df_filtered_sources[df_filtered_sources["country_name"].notna() &
                                     df_filtered_sources["country_name"].str.contains(selected_country, case=False)]
    
    if not df_country.empty:
        st.subheader(f"📊 Pollution Data for {selected_country}")
        st.dataframe(df_country[["location_id","country_name","pollution_source","pm2_5","pm10","no2","so2","o3","co","aqi"]])

        # Example: Future AQI prediction (number only)
        # Replace this with your ML model logic
        predicted_aqi = df_country["aqi"].mean() + 0.5  # dummy prediction
        st.metric(f"🔮 Predicted AQI for {selected_country}", f"{predicted_aqi:.2f}")

        # High-risk alert for that country
        high_risk_country = df_country[df_country["aqi"] > aqi_threshold]
        if not high_risk_country.empty:
            st.warning(f"{high_risk_country.shape[0]} locations in {selected_country} exceed safe AQI thresholds!")
    else:
        st.info(f"No data found for country: {selected_country}")

# ----------------- DOWNLOAD OPTION -----------------
st.subheader("📥 Download Pollution Report")
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df_filtered_sources)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='pollution_report.csv',
    mime='text/csv',
)
