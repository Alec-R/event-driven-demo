# setup_db.py
import psycopg2
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    conn_params = {
        'dbname': 'alertdb',
        'user': 'admin',
        'password': 'admin123',
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = os.path.join('schema', 'init.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        logger.info("Database schema initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database()