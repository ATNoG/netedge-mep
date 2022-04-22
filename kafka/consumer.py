from kafka import KafkaConsumer
consumer = KafkaConsumer("mep",bootstrap_servers='localhost:9093',
                         auto_offset_reset="smallest",
                         enable_auto_commit=True,
                         group_id="test")

for msg in consumer:
    print(f"Received message {msg.value.decode()} in topic {msg.topic} create with timestamp {msg.timestamp}")