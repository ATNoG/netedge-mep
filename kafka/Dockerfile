FROM python:3.9

RUN useradd -m -d /home/kafka kafka
RUN ["apt-get", "update"]
COPY ./kafka-dump.py /home/kafka
USER kafka
RUN mkdir /home/kafka/dump
ENV PATH="$PATH:/home/kafka/.local/bin"
RUN ["pip","install","kafka-python"]

ENTRYPOINT ["python3"]
CMD ["/home/kafka/kafka-dump.py"]
