# dags/system_monitoring_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from kafka.admin import KafkaAdminClient
from kafka import KafkaConsumer

from datetime import datetime, timedelta
import json
import psutil
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_kafka_health(**context):
    """Monitor Kafka health and metrics"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=['kafka:9092'],
            client_id='airflow-monitor'
        )
        
        # Get topic metrics
        topics = admin_client.list_topics()
        
        # Get consumer group lag
        consumer = KafkaConsumer(
            bootstrap_servers=['kafka:9092'],
            group_id='monitor-group'
        )
        
        metrics = {
            'topic_count': len(topics),
            'consumer_groups': len(consumer.list_consumer_groups()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save metrics
        metrics_path = f"/opt/airflow/data/metrics/kafka_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
            
    except Exception as e:
        raise Exception(f"Kafka health check failed: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
        if 'admin_client' in locals():
            admin_client.close()

def check_postgres_health(**context):
    """Monitor PostgreSQL health and metrics"""
    pg_hook = PostgresHook(postgres_conn_id='transaction_db')
    
    # Get database statistics
    metrics = {}
    
    # Database size
    size_query = """
    SELECT pg_database_size(current_database()) as db_size,
           pg_size_pretty(pg_database_size(current_database())) as db_size_pretty
    """
    metrics['database_size'] = pg_hook.get_first(size_query)[1]
    
    # Table statistics
    table_stats_query = """
    SELECT relname as table_name,
           n_live_tup as row_count,
           n_dead_tup as dead_tuples
    FROM pg_stat_user_tables
    """
    metrics['table_stats'] = pg_hook.get_records(table_stats_query)
    
    # Save metrics
    metrics_path = f"/opt/airflow/data/metrics/postgres_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)

with DAG(
    'system_monitoring',
    default_args=default_args,
    description='Monitor system health and metrics',
    schedule_interval='*/15 * * * *',  # Run every 15 minutes
    catchup=False
) as dag:

    kafka_health = PythonOperator(
        task_id='check_kafka_health',
        python_callable=check_kafka_health,
        provide_context=True,
    )

    postgres_health = PythonOperator(
        task_id='check_postgres_health',
        python_callable=check_postgres_health,
        provide_context=True,
    )

    [kafka_health, postgres_health]