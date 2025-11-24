"""
Example DAG for energy demand data pipeline
This DAG fetches energy data from APIs, processes it, and stores in PostgreSQL
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import pandas as pd
import logging

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'energy_demand_etl',
    default_args=default_args,
    description='ETL pipeline for energy demand forecasting',
    schedule_interval='0 * * * *',  # Run every hour
    catchup=False,
    tags=['energy', 'etl', 'forecast'],
)


def fetch_energy_data(**context):
    """
    Fetch energy demand data from API
    """
    logging.info("Fetching energy demand data from API")
    
    # Example API call - replace with actual API
    # api_url = "https://api.energy.com/demand"
    # response = requests.get(api_url, headers={"Authorization": f"Bearer {API_KEY}"})
    
    # For now, create sample data
    sample_data = {
        'timestamp': datetime.now(),
        'demand_mw': 5000.0,
        'region': 'madrid'
    }
    
    # Push to XCom for next task
    context['ti'].xcom_push(key='energy_data', value=sample_data)
    logging.info(f"Fetched data: {sample_data}")


def fetch_weather_data(**context):
    """
    Fetch weather data from API
    """
    logging.info("Fetching weather data from API")
    
    # Example API call - replace with actual API
    sample_data = {
        'timestamp': datetime.now(),
        'temperature': 22.5,
        'humidity': 65.0,
        'wind_speed': 10.5,
        'precipitation': 0.0,
        'region': 'madrid'
    }
    
    context['ti'].xcom_push(key='weather_data', value=sample_data)
    logging.info(f"Fetched weather data: {sample_data}")


def transform_and_load_data(**context):
    """
    Transform data and load into PostgreSQL
    """
    ti = context['ti']
    
    # Pull data from XCom
    energy_data = ti.xcom_pull(key='energy_data', task_ids='fetch_energy_data')
    weather_data = ti.xcom_pull(key='weather_data', task_ids='fetch_weather_data')
    
    logging.info("Transforming and loading data to database")
    
    # Get PostgreSQL connection
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Insert energy data
        cursor.execute("""
            INSERT INTO production.energy_demand (timestamp, demand_mw, region)
            VALUES (%s, %s, %s)
            ON CONFLICT (timestamp, region) DO UPDATE
            SET demand_mw = EXCLUDED.demand_mw,
                updated_at = CURRENT_TIMESTAMP
        """, (energy_data['timestamp'], energy_data['demand_mw'], energy_data['region']))
        
        # Insert weather data
        cursor.execute("""
            INSERT INTO production.weather_data (timestamp, temperature, humidity, wind_speed, precipitation, region)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp, region) DO UPDATE
            SET temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                wind_speed = EXCLUDED.wind_speed,
                precipitation = EXCLUDED.precipitation,
                updated_at = CURRENT_TIMESTAMP
        """, (
            weather_data['timestamp'],
            weather_data['temperature'],
            weather_data['humidity'],
            weather_data['wind_speed'],
            weather_data['precipitation'],
            weather_data['region']
        ))
        
        conn.commit()
        logging.info("Data successfully loaded to database")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


# Define tasks
task_fetch_energy = PythonOperator(
    task_id='fetch_energy_data',
    python_callable=fetch_energy_data,
    dag=dag,
)

task_fetch_weather = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=dag,
)

task_transform_load = PythonOperator(
    task_id='transform_and_load',
    python_callable=transform_and_load_data,
    dag=dag,
)

# Set task dependencies
[task_fetch_energy, task_fetch_weather] >> task_transform_load
