from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
from datetime import datetime
import os
import json

OUTPUT_DIR = "/opt/airflow/data/raw"
RAW_DATA_DIR = "/opt/airflow/data/raw"
PROCESSED_DATA_DIR = "/opt/airflow/data/processed"
FINAL_PATH = "/opt/airflow/data/dashboard_csv"
JSON_PATH = "/opt/airflow/config/cities.json"




default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="weather_dag",
    description="ETL pipeline for italian weather",
    default_args=default_args,
    schedule="@daily",  # esecuzione giornaliera
    start_date=datetime(2025, 10, 20),
    catchup=False
)



def extract_function():
   
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    with open(JSON_PATH, "r") as f:
        cities = json.load(f)

    for city in cities:

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={city['lat']}&longitude={city['lon']}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=Europe/Rome"
        )


        response = requests.get(url)
        data = response.json()

    
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])


        df = pd.DataFrame({
            "date": dates,
            "city": city['name'],
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precipitation": precip
        })

        file_path = os.path.join(OUTPUT_DIR, f"{city['name'].lower()}_{today}.csv")
        df.to_csv(file_path, index=False)

    print(f"Dati meteo salvati in: {file_path}")
    pass

def transform_function():
    
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)     

    for file in os.listdir(RAW_DATA_DIR):
        raw_path = os.path.join(RAW_DATA_DIR, file)
        df = pd.read_csv(raw_path)
        df = df.drop_duplicates()
        df = df.dropna()

        city_name = str(df['city'][0])
        avg_min_temp = round(df['temp_min'].mean(), 2)
        avg_max_temp = round(df['temp_max'].mean(), 2)
        avg_daily_temp = round((avg_min_temp + avg_max_temp)/2, 2)
        avg_precipitation = round(df['precipitation'].mean(), 2)



        stats_df = pd.DataFrame([{
            "city": city_name,
            "avg_min_temp": avg_min_temp,
            "avg_max_temp": avg_max_temp,
            "avg_daily_temp": avg_daily_temp, 
            "avg_precipitation": avg_precipitation
        }])

        processed_path = os.path.join(PROCESSED_DATA_DIR, f"{city_name.lower()}_stats.csv")
            
        stats_df.to_csv(processed_path, index=False)
        
        pass

def aggregate_function():

    os.makedirs(FINAL_PATH, exist_ok=True)

    all_df = []
    for f in os.listdir(PROCESSED_DATA_DIR):
        df_temp_path = os.path.join(PROCESSED_DATA_DIR, f)
        df_temp = pd.read_csv(df_temp_path)
        all_df.append(df_temp) 
        df_agg = pd.concat(all_df, ignore_index=True)
        df_agg.to_csv(os.path.join(FINAL_PATH, "aggregated_stats.csv"), index=False)

    pass


extract_task = PythonOperator(
    task_id="extract_meteo_data",
    python_callable=extract_function,
    dag=dag
)

transform_task = PythonOperator(
    task_id="transform_meteo_data",
    python_callable=transform_function,
    dag=dag
)

aggregate_task = PythonOperator(
    task_id="aggregate_csv",
    python_callable=aggregate_function,
    dag=dag
)

# Sequenza dei task
extract_task >> transform_task >> aggregate_task