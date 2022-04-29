FROM python:3.9

LABEL org.opencontainers.image.source="https://github.com/ATNOG/netedge-mep"

RUN useradd -m -d /home/netedge netedge
RUN ["apt-get", "update"]
COPY ./ /home/netedge
USER netedge
ENV PATH="$PATH:/home/netedge/.local/bin"
RUN ["pip","install","-r","/home/netedge/requirements.txt"]

ENTRYPOINT ["python3"]
CMD ["/home/netedge/main.py","--mongodb_addr","127.0.0.1","--mongodb_database","mep"]
