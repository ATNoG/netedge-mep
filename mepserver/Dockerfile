FROM python:3.9

RUN useradd -m -d /home/netedge netedge
RUN ["apt-get", "update"]
ADD . /home/netedge
USER netedge
ENV PATH="/home/netedge/.local/bin:$PATH"
RUN ["pip","install","-r","/home/netedge/requirements.txt"]

ENTRYPOINT [ "python3" ]
CMD ["/home/netedge/main.py]