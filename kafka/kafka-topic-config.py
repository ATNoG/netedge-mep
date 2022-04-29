from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType
import re
import socket
"""
Obtains config resource
In this specific case it obtains and prints config resource retetion
"""

kafka_ip = socket.gethostbyname("kafka")
kafka_port = 9092
admin_client = KafkaAdminClient(bootstrap_servers=[f'{kafka_ip}:{kafka_port}'])
topics = admin_client.list_topics()
topic_processes = []
for topic in topics:
	if re.match(r"^(?!__.*).*",topic):
		configs = admin_client.describe_configs(config_resources=[ConfigResource(ConfigResourceType.TOPIC, topic)])
		"""
		Example of index and data in resources[0][4]
		0 ('compression.type', 'producer', False, 5, False, [])
		1 ('leader.replication.throttled.replicas', '', False, 5, False, [])
		2 ('min.insync.replicas', '1', False, 5, False, [])
		3 ('message.downconversion.enable', 'true', False, 5, False, [])
		4 ('segment.jitter.ms', '0', False, 5, False, [])
		5 ('cleanup.policy', 'delete', False, 5, False, [])
		6 ('flush.ms', '9223372036854775807', False, 5, False, [])
		7 ('follower.replication.throttled.replicas', '', False, 5, False, [])
		8 ('segment.bytes', '1073741824', False, 4, False, [])
		9 ('retention.ms', '604800000', False, 5, False, [])
		10 ('flush.messages', '9223372036854775807', False, 5, False, [])
		11 ('message.format.version', '3.0-IV1', False, 5, False, [])
		12 ('max.compaction.lag.ms', '9223372036854775807', False, 5, False, [])
		13 ('file.delete.delay.ms', '60000', False, 5, False, [])
		14 ('max.message.bytes', '1048588', False, 5, False, [])
		15 ('min.compaction.lag.ms', '0', False, 5, False, [])
		16 ('message.timestamp.type', 'CreateTime', False, 5, False, [])
		17 ('preallocate', 'false', False, 5, False, [])
		18 ('index.interval.bytes', '4096', False, 5, False, [])
		19 ('min.cleanable.dirty.ratio', '0.5', False, 5, False, [])
		20 ('unclean.leader.election.enable', 'false', False, 5, False, [])
		21 ('retention.bytes', '-1', False, 5, False, [])
		22 ('delete.retention.ms', '86400000', False, 5, False, [])
		23 ('segment.ms', '604800000', False, 5, False, [])
		24 ('message.timestamp.difference.max.ms', '9223372036854775807', False, 5, False, [])
		25 ('segment.index.bytes', '10485760', False, 5, False, [])
		"""
		retention = configs[0].resources[0][4][9]
		print(f"Topic {topic} has retention {retention}")
