from datetime import datetime, timedelta
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from typing import List, Dict, Any
import psycopg2
from sqlalchemy import create_engine


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'currency_data_scraper',
    default_args=default_args,
    description='Update data in db',
    schedule_interval=timedelta(days=1),
)

# Reads data about currency exchange rates against the dollar from a website https://apilayer.com
def extract_data() -> dict:
    currency_codes = ["AUD", "GBP", "BRL", "HUF", "HKD", "DKK", "EUR", "ILS", "INR", "IDR",
                    "CAD", "CNY", "MYR", "MXN", "NZD", "NOK", "PKR", "PLN", "RUB", "SGD",
                    "TWD", "THB", "TRY", "PHP", "CZK", "CLP", "SEK", "CHF", "ZAR", "KRW",
                    "UAH", "JPY"]
    currency_codes_str = ",".join(currency_codes)

    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={currency_codes_str}&base=USD"
    #use api_key from https://apilayer.com/marketplace/exchangerates_data-api
    #api_key = "api_key"
    headers = {
        "apikey": api_key
    }

    response = requests.request("GET", url, headers=headers)
    currency_data = response.json()

    return currency_data

def transform_data(currency_data: pd.DataFrame) -> List[Dict[str, Any]]:
    # Changes the data for storage in the database
    currencies_dict = {
        "AUD": "Australian Dollar",
        "GBP": "British Pound",
        "BRL": "Brazilian Real",
        "HUF": "Hungarian Forint",
        "HKD": "Hong Kong Dollar",
        "DKK": "Danish Krone",
        "EUR": "Euro",
        "ILS": "Israeli New Shekel",
        "INR": "Indian Rupee",
        "IDR": "Indonesian Rupiah",
        "CAD": "Canadian Dollar",
        "CNY": "Chinese Yuan",
        "MYR": "Malaysian Ringgit",
        "MXN": "Mexican Peso",
        "NZD": "New Zealand Dollar",
        "NOK": "Norwegian Krone",
        "PKR": "Pakistani Rupee",
        "PLN": "Polish Zloty",
        "RUB": "Russian Ruble",
        "SGD": "Singapore Dollar",
        "TWD": "New Taiwan Dollar",
        "THB": "Thai Baht",
        "TRY": "Turkish Lira",
        "PHP": "Philippine Peso",
        "CZK": "Czech Koruna",
        "CLP": "Chilean Peso",
        "SEK": "Swedish Krona",
        "CHF": "Swiss Franc",
        "ZAR": "South African Rand",
        "KRW": "South Korean Won",
        "UAH": "Ukrainian Hryvnia",
        "JPY": "Japanese Yen"
    }
    data = pd.DataFrame(currency_data)
    data = data.reset_index()
    data = data.drop(['success', 'date'], axis=1)
    data = data.rename(columns={'rates': 'rate', 'index': 'currency_code', 'timestamp': 'time'})
    data['currency_name'] = data['currency_code'].map(currencies_dict)
    currency_data = data.reindex(columns=['base', 'currency_code', 'currency_name', 'rate', 'time'])
    return currency_data.to_dict(orient='records')

def load_data(currency_data: List[dict]):
    
    currency_data = pd.DataFrame(currency_data)
    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow"
    )

    engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
    currency_data.to_sql('exchange_rate', engine, if_exists='replace')

    with conn.cursor() as cursor:
        for index, row in currency_data.iterrows():
            cursor.execute("""
                INSERT INTO exchange_rate (base, currency_code, currency_name, rate, time) VALUES (%s, %s, %s, %s, %s)
            """, (row['base'], row['currency_code'], row['currency_name'], row['rate'], row['time']))
    conn.commit()
    conn.close()

t1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    op_args=[t1.output],
    dag=dag
)

t3 = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    op_args=[t2.output],
    dag=dag
)

t1 >> t2 >> t3