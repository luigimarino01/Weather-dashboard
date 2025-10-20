import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page title
st.set_page_config(page_title="Italy Weather Dashboard")
st.title("🌤️ Italy Weather Dashboard")
st.text("*The statistics are based on the last seven days*")

# Paths
RAW_DATA_DIR = "../airflow/data/raw"
AGGREGATED_CSV = "../airflow/data/dashboard_csv/aggregated_stats.csv"

# Load aggregated CSV for metrics
df_agg = pd.read_csv(AGGREGATED_CSV)

# Single city selection
cities = df_agg["city"].unique()
selected_city = st.selectbox("Select a city", options=cities, index=0)

# Display metrics (averages)
city_row = df_agg[df_agg["city"] == selected_city].iloc[0]
st.header(f"Average Statistics for {selected_city}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Min Temperature", f"{city_row['avg_min_temp']:.2f}°C")
col2.metric("Max Temperature", f"{city_row['avg_max_temp']:.2f}°C")
col3.metric("Daily Temperature", f"{city_row['avg_daily_temp']:.2f}°C")
col4.metric("Precipitation", f"{city_row['avg_precipitation']:.2f} mm")

# Load raw CSV for selected city
raw_files = [f for f in os.listdir(RAW_DATA_DIR) if selected_city.lower() in f.lower()]
if not raw_files:
    st.warning("No raw data found for this city.")
else:
    # Take the latest file (by date in filename)
    raw_files.sort()
    latest_file = raw_files[-1]
    df_raw = pd.read_csv(os.path.join(RAW_DATA_DIR, latest_file))

    # Ensure only last 7 days
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_last7 = df_raw.sort_values('date').tail(7)

    # Line chart for temperatures
    st.header("🌡️ Temperature Trend (Last 7 Days)")
    st.line_chart(df_last7.set_index('date')[['temp_min','temp_max']])

    # Bar chart for precipitation
    st.header("🌧️ Precipitation (Last 7 Days)")
    st.bar_chart(df_last7.set_index('date')['precipitation'])
