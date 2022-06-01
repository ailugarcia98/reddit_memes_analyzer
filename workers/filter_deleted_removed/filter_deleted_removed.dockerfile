FROM ubuntu:20.04

RUN apt update && apt install python3 python3-pip -y
RUN pip3 install pika

COPY filter_deleted_removed.py /
COPY main.py /
CMD ["python3", "./main.py"]