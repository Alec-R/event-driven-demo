# consumer/transaction_consumer.py
from kafka import KafkaConsumer
import json

import uuid
from datetime import datetime

import logging
import sys
import os

import signal

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import DatabaseConnection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionConsumer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.consumer = self._create_consumer()
        self.running = True
        self._setup_signal_handling()

    def _setup_signal_handling(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}. Starting graceful shutdown...")
        self.running = False

    def _create_consumer(self):
        """Create and return a Kafka consumer"""
        try:
            consumer = KafkaConsumer(
                'transactions',
                bootstrap_servers=['localhost:9092'],
                group_id='transaction-processor-group',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Kafka consumer created successfully")
            return consumer
        except Exception as e:
            logger.error(f"Error creating Kafka consumer: {e}")
            raise

    def check_for_alerts(self, transaction):
        """
        Check transaction for conditions that should trigger alerts
        Returns list of (alert_type, message) tuples
        """
        alerts = []
        
        # Alert on large transactions
        if transaction['amount'] > 1000:
            alerts.append(
                ('LARGE_TRANSACTION', 
                 f"Large transaction of ${transaction['amount']} detected for account {transaction['account_id']}")
            )
        
        # Alert on withdrawals
        if transaction['transaction_type'] == 'WITHDRAWAL':
            alerts.append(
                ('WITHDRAWAL_ALERT',
                 f"Withdrawal of ${transaction['amount']} from account {transaction['account_id']}")
            )
        
        return alerts

    def process_transaction(self, transaction):
        """Process a single transaction"""
        try:
            # Store transaction
            transaction_id = self.db.insert_transaction(transaction)
            logger.info(f"Stored transaction {transaction_id}")
            
            # Check for alerts
            alerts = self.check_for_alerts(transaction)
            
            # Store any alerts
            for alert_type, message in alerts:
                alert_id = str(uuid.uuid4())
                self.db.insert_alert(alert_id, transaction_id, alert_type, message)
                logger.info(f"Generated alert: {alert_type} - {message}")
            
            return True
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return False

    def run(self):
        """Main consumer loop with graceful shutdown"""
        logger.info("Starting transaction consumer...")
        self.db.connect()
        
        try:
            while self.running:
                # Poll with timeout to allow checking running flag
                messages = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, records in messages.items():
                    for record in records:
                        if not self.running:
                            break
                        
                        transaction = record.value
                        logger.info(f"Received transaction: {transaction}")
                        
                        if self.process_transaction(transaction):
                            logger.info("Successfully processed transaction")
                        else:
                            logger.error("Failed to process transaction")
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        try:
            # Commit any pending offsets
            self.consumer.commit()
            
            # Close consumer and DB connection
            self.consumer.close()
            self.db.disconnect()
            
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    consumer = TransactionConsumer()
    consumer.run()

if __name__ == "__main__":
    main()