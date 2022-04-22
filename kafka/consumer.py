from kafka import KafkaConsumer
import argparse
def main(group):
	consumer = KafkaConsumer("mep",bootstrap_servers='localhost:9093',
	                         auto_offset_reset="smallest",
	                         enable_auto_commit=True,
	                         group_id=group)

	for msg in consumer:
	    print(f"Group {group} - Received message {msg.value.decode()} in topic {msg.topic} create with timestamp {msg.timestamp}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser("Consumer group example")
	parser.add_argument("--group",type=str,required=False,default="test")
	args = parser.parse_args()
	main(args.group)
