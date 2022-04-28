from kafka import KafkaAdminClient, KafkaConsumer
from multiprocessing import Process
import re
import sys
import time
import socket

def dump_topic_to_file(kafka_ip,kafka_port,topic):
    consumer = KafkaConsumer(topic,bootstrap_servers=f'{kafka_ip}:{kafka_port}',
	                         auto_offset_reset="smallest",
	                         enable_auto_commit=True,
	                         group_id="timing")
    with open(f"dump/{topic}","a+") as outfile:
        for msg in consumer:            
            outfile.write(f"Received message {msg.value.decode()} in topic {msg.topic} create with timestamp {msg.timestamp}\n")
            
kafka_ip = socket.gethostbyname("kafka")
kafka_port = 9092
admin_client = KafkaAdminClient(bootstrap_servers=[f'{kafka_ip}:{kafka_port}'])
topics = admin_client.list_topics()
topic_processes = []

# Improper thread doesn't close file descriptor nor stops gracefully but does the job for what we require
for topic in topics:
    if re.match(r"^(?!__.*).*",topic):
        print(f"Starting process for {topic}")
        p = Process(target=dump_topic_to_file, args=(kafka_ip,kafka_port,topic))
        topic_processes.append(p)
        p.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt as e:
        for process in topic_processes:
            process.join()
        exit()