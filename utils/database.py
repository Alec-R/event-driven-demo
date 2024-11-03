# utils/database.py
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.conn_params = {
            'dbname': 'alertdb',
            'user': 'admin',
            'password': 'admin123',
            'host': 'localhost',
            'port': '5432'
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def insert_transaction(self, transaction):
        try:
            query = """
                INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING transaction_id
            """
            self.cursor.execute(query, (
                transaction['transaction_id'],
                transaction['account_id'],
                transaction['transaction_type'],
                transaction['amount'],
                datetime.fromisoformat(transaction['timestamp'])
            ))
            self.conn.commit()
            return self.cursor.fetchone()['transaction_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting transaction: {e}")
            raise

    def insert_alert(self, alert_id, transaction_id, alert_type, message):
        try:
            query = """
                INSERT INTO alerts (alert_id, transaction_id, alert_type, alert_message)
                VALUES (%s, %s, %s, %s)
                RETURNING alert_id
            """
            self.cursor.execute(query, (alert_id, transaction_id, alert_type, message))
            self.conn.commit()
            return self.cursor.fetchone()['alert_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting alert: {e}")
            raise

    def get_recent_transactions(self, limit=10):
        try:
            query = """
                SELECT * FROM transactions
                ORDER BY timestamp DESC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {e}")
            raise