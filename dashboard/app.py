import streamlit as st
import pandas as pd

# Set page title
st.set_page_config(page_title="Italy Weather Dashboard")
st.title("🌤️ Italy Weather Dashboard")
st.text("*The statistics are based on the last seven days")

# Load aggregated CSV
df = pd.read_csv("../airflow/data/dashboard_csv/aggregated_stats.csv")

# Single city selection
cities = df["city"].unique()
selected_city = st.selectbox("Select a city", options=cities, index=0)

# Get the row for the selected city
city_row = df[df["city"] == selected_city].iloc[0]

# Display metrics
st.header(f"Average Statistics for {selected_city}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Min Temperature", f"{city_row['avg_min_temp']:.2f}°C")
col2.metric("Max Temperature", f"{city_row['avg_max_temp']:.2f}°C")
col3.metric("Daily Temperature", f"{city_row['avg_daily_temp']:.2f}°C")
col4.metric("Precipitation", f"{city_row['avg_precipitation']:.2f} mm")

# Bar chart for temperatures
st.header("🌡️ Temperature Overview")
st.bar_chart({
    "Min Temp": [city_row['avg_min_temp']],
    "Max Temp": [city_row['avg_max_temp']],
    "Daily Temp": [city_row['avg_daily_temp']]
})

# Bar chart for precipitation
st.header("🌧️ Precipitation")
st.bar_chart([city_row['avg_precipitation']])


