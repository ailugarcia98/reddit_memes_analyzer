FROM ubuntu:20.04

RUN apt update && apt install python3 python3-pip -y
RUN pip3 install pika

COPY find_max_sent_avg.py /
COPY main.py /
CMD ["python3", "./main.py"]