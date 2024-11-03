# dags/transaction_reporting_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from datetime import datetime, timedelta
import pandas as pd
import json
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

def generate_daily_report(**context):
    """Generate daily transaction report"""
    pg_hook = PostgresHook(postgres_conn_id='transaction_db')
    
    # Get yesterday's date
    execution_date = context['execution_date']
    report_date = execution_date - timedelta(days=0)
    
    # Query for daily statistics
    sql = """
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as total_transactions,
        SUM(CASE WHEN transaction_type = 'DEPOSIT' THEN 1 ELSE 0 END) as deposits,
        SUM(CASE WHEN transaction_type = 'WITHDRAWAL' THEN 1 ELSE 0 END) as withdrawals,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        COUNT(DISTINCT account_id) as unique_accounts
    FROM transactions 
    WHERE DATE(timestamp) = %s
    GROUP BY DATE(timestamp)
    """
    
    df = pd.read_sql(sql, pg_hook.get_conn(), params=[report_date])
    
    # Save report
    report_path = f"/opt/airflow/data/reports/daily_{report_date.strftime('%Y%m%d')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    report_data = df.to_dict('records')[0] if not df.empty else {}
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)

def analyze_alerts(**context):
    """Analyze alerts for patterns"""
    pg_hook = PostgresHook(postgres_conn_id='transaction_db')
    execution_date = context['execution_date']
    report_date = execution_date - timedelta(days=1)
    
    sql = """
    SELECT 
        alert_type,
        COUNT(*) as alert_count,
        AVG(t.amount) as avg_transaction_amount
    FROM alerts a
    JOIN transactions t ON a.transaction_id = t.transaction_id
    WHERE DATE(a.created_at) = %s
    GROUP BY alert_type
    """
    
    df = pd.read_sql(sql, pg_hook.get_conn(), params=[report_date])
    
    # Save alert analysis
    report_path = f"/opt/airflow/data/reports/alerts_{report_date.strftime('%Y%m%d')}.json"
    with open(report_path, 'w') as f:
        json.dump(df.to_dict('records'), f, indent=2, default=str)

with DAG(
    'transaction_reporting',
    default_args=default_args,
    description='Daily transaction reporting and analysis',
    schedule_interval='0 1 * * *',  # Run at 1 AM daily
    catchup=False
) as dag:

    # Create daily report
    create_report = PythonOperator(
        task_id='generate_daily_report',
        python_callable=generate_daily_report,
        provide_context=True,
    )

    # Analyze alerts
    analyze_daily_alerts = PythonOperator(
        task_id='analyze_alerts',
        python_callable=analyze_alerts,
        provide_context=True,
    )

    # Cleanup old reports (keep last 30 days)
    cleanup_old_reports = PostgresOperator(
        task_id='cleanup_old_reports',
        postgres_conn_id='transaction_db',
        sql="""
        DELETE FROM transactions 
        WHERE timestamp < NOW() - INTERVAL '30 days'
        """
    )

    create_report >> analyze_daily_alerts >> cleanup_old_reports