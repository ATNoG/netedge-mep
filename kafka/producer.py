from kafka import KafkaProducer
import time
producer = KafkaProducer(bootstrap_servers='0.0.0.0:9093')
for _ in range(100):
    producer.send('mep', b'some_message_bytes')
    producer.flush()
