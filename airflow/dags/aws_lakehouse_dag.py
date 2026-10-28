"""Daily AWS lakehouse DAG (local steps, no real AWS calls).

Task order mirrors the pipeline: generate -> bronze -> silver ->
gold -> quality. In real AWS, the local Python steps would be
replaced by Glue jobs / EMR-Spark steps; the order, retries, and
quality gate stay the same.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.pipeline import run_pipeline

default_args = {
    "owner": "sai",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def _run_pipeline(**_context):
    counts = run_pipeline()
    print(counts)


with DAG(
    dag_id="aws_data_lakehouse_daily",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["aws", "lakehouse", "s3", "glue", "athena"],
) as dag:
    run_lakehouse = PythonOperator(
        task_id="run_bronze_silver_gold_quality",
        python_callable=_run_pipeline,
    )
