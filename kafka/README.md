# Deploy kafka in docker 
```bash
# Docker compose has an EXTERNAL Endpoint to be accessible from outside the docker network for development/testing purposes
$ docker-compose up -d
```

# Create topic
```bash
sudo docker exec -it <kafka_container> /opt/bitnami/kafka/bin/kafka-topics.sh --create --topic <topic_name> --bootstrap-server <ip>:<port>
```