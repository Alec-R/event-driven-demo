# producer/transaction_producer.py
from kafka import KafkaProducer

import time
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema.models import Transaction

def create_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return None

def main():
    producer = create_kafka_producer()
    if not producer:
        return

    print("Starting to generate transactions...")
    try:
        while True:
            # Create a random transaction
            transaction = Transaction.create_random()
            
            # Send to Kafka
            producer.send('transactions', value=transaction.__dict__)
            print(f"Sent transaction: {transaction}")
            
            # Wait for 2 seconds before next transaction
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping transaction generator...")
        producer.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        producer.close()

if __name__ == "__main__":
    main()