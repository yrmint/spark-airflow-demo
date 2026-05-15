from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import random

def failing_task():
    """Dummy task that fails sometimes"""
    if random.random() < 0.6:  # 60% chance of failure
        raise Exception("Random error for retry testing")
    print("failing_task executed successfully")

with DAG(
        dag_id="spark_ml_clickhouse_demo",
        start_date=datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
        default_args={
            "retries": 3,
            "retry_delay": timedelta(minutes=1),
            "owner": "demo",
        },
        tags=["spark", "clickhouse", "ml"],
) as dag:

    start = PythonOperator(
        task_id="start",
        python_callable=lambda: print("Pipeline started")
    )

    spark_ml_task = SparkSubmitOperator(
        task_id="spark_linear_regression",
        application="/opt/spark_jobs/linear_regression.py",
        conn_id="spark_default",
        conf={
            "spark.executor.instances": "2",
            "spark.executor.cores": "1",
            "spark.executor.memory": "1g",
        },
        jars="/opt/spark/jars/clickhouse-jdbc.jar",
        verbose=True,
        driver_memory="1g",
        executor_memory="1g",
    )

    failing_task_op = PythonOperator(
        task_id="failing_task_with_retry",
        python_callable=failing_task
    )

    end = PythonOperator(
        task_id="end",
        python_callable=lambda: print("Pipeline ended")
    )

    start >> spark_ml_task >> failing_task_op >> end
