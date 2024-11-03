# test_consumer.py
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Starting consumer... waiting for messages")
for message in consumer:
    print(f"Received: {message.value}")